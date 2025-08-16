"""
BongoCat Command Line Interface

Main CLI entry point for BongoCat web scraping framework.
"""

import click
import json
import os
from typing import Dict, Any

from .core_scraper.scraper import BongoCat
from .data_parser.parser import DataParser
from .output_handler.handler import OutputHandler
from .consistency_checker.checker import ConsistencyChecker
from .config_manager.manager import ConfigManager


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """BongoCat - Advanced Web Scraping Framework"""
    pass


@cli.command()
@click.argument('url')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output', '-o', default='output.json', help='Output file path')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv', 'xml', 'html']), help='Output format')
@click.option('--browser', is_flag=True, help='Use browser for JavaScript rendering')
@click.option('--selectors', help='JSON string of CSS selectors')
@click.option('--wait-time', default=2, help='Wait time for page load (seconds)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def scrape(url, config, output, format, browser, selectors, wait_time, verbose):
    """Scrape a single URL"""
    try:
        # Parse selectors if provided
        selector_dict = {}
        if selectors:
            selector_dict = json.loads(selectors)
        
        # Initialize scraper
        scraper = BongoCat(config_path=config, use_browser=browser)
        
        if verbose:
            click.echo(f"🔍 Scraping: {url}")
            click.echo(f"📁 Output: {output}")
            click.echo(f"📊 Format: {format}")
        
        # Perform scrape
        result = scraper.scrape(
            url, 
            selectors=selector_dict,
            wait_time=wait_time
        )
        
        # Export result
        if result['status'] == 'success':
            filepath = scraper.export(result, format, output)
            if verbose:
                click.echo(f"✅ Successfully scraped and saved to {filepath}")
            else:
                click.echo(f"Saved to {filepath}")
        else:
            click.echo(f"❌ Scraping failed: {result.get('error', 'Unknown error')}", err=True)
            return 1
        
        # Clean up
        scraper.close()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@cli.command()
@click.argument('urls_file')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--output-dir', '-o', default='output', help='Output directory')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv', 'xml', 'html']), help='Output format')
@click.option('--concurrent', default=5, help='Number of concurrent scrapers')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch(urls_file, config, output_dir, format, concurrent, verbose):
    """Scrape multiple URLs from file"""
    try:
        # Read URLs from file
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if verbose:
            click.echo(f"📋 Found {len(urls)} URLs to scrape")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize scraper
        scraper = BongoCat(config_path=config)
        
        # Process URLs
        results = scraper.scrape_multiple(urls)
        
        # Save results
        for i, result in enumerate(results):
            filename = f"result_{i+1}.{format}"
            filepath = os.path.join(output_dir, filename)
            
            if result.get('status') == 'success':
                scraper.export(result, format, filepath)
                if verbose:
                    click.echo(f"✅ Saved {result['url']} to {filepath}")
            else:
                if verbose:
                    click.echo(f"❌ Failed {result['url']}: {result.get('error', 'Unknown error')}")
        
        scraper.close()
        
        if verbose:
            success_count = len([r for r in results if r.get('status') == 'success'])
            click.echo(f"🎉 Completed: {success_count}/{len(urls)} successful")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@cli.command()
@click.argument('content_file')
@click.option('--content-type', default='auto', help='Content type (html, json, xml, csv, auto)')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', default='json', help='Output format')
@click.option('--schema', help='JSON schema file for structured extraction')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def parse(content_file, content_type, output, format, schema, verbose):
    """Parse content from file"""
    try:
        # Read content
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Load schema if provided
        schema_dict = {}
        if schema:
            with open(schema, 'r') as f:
                schema_dict = json.load(f)
        
        if verbose:
            click.echo(f"📄 Parsing {content_file} as {content_type}")
        
        # Parse content
        parser = DataParser()
        
        if schema_dict:
            result = parser.extract_structured_data(content, schema_dict)
        else:
            result = parser.parse(content, content_type)
        
        # Output result
        if output:
            handler = OutputHandler()
            filepath = handler.export(result, format, output)
            if verbose:
                click.echo(f"💾 Saved parsed data to {filepath}")
        else:
            click.echo(json.dumps(result, indent=2))
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@cli.command()
@click.option('--output', '-o', default='consistency_report.json', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def check(output, verbose):
    """Run consistency check on BongoCat project"""
    try:
        if verbose:
            click.echo("🔍 Running BongoCat consistency check...")
        
        # Run consistency check
        checker = ConsistencyChecker()
        results = checker.run_full_consistency_check()
        
        # Export detailed report
        report_file = checker.export_detailed_report(output)
        
        if verbose:
            # Display summary
            stats = results.get('statistics', {})
            click.echo(f"\n📊 Results:")
            click.echo(f"  Files analyzed: {stats.get('total_files', 0)}")
            click.echo(f"  Components: {stats.get('total_components', 0)}")
            click.echo(f"  Issues found: {stats.get('issues_found', 0)}")
            click.echo(f"  Issues fixed: {stats.get('issues_fixed', 0)}")
            click.echo(f"  Duration: {stats.get('duration_seconds', 0):.2f}s")
            click.echo(f"\n📁 Detailed report saved to: {report_file}")
        else:
            click.echo(f"Consistency check complete. Report saved to: {report_file}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@cli.command()
@click.option('--config-file', default='config.json', help='Configuration file to create')
def init(config_file):
    """Initialize BongoCat configuration"""
    try:
        config_manager = ConfigManager()
        default_config = config_manager.get_default_config()
        
        # Save default configuration
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        click.echo(f"✅ Created configuration file: {config_file}")
        click.echo("Edit this file to customize BongoCat settings.")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        return 1


@cli.command()
def version():
    """Show BongoCat version information"""
    click.echo("BongoCat Web Scraping Framework")
    click.echo("Version: 1.0.0")
    click.echo("Author: BongoCat Team")
    click.echo("Homepage: https://github.com/bongocat/bongocat")


if __name__ == '__main__':
    cli()