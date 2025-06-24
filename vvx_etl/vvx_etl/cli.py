from vvx_etl.source_detection_etl import pipeline
import click


@click.command()
@click.option("--config", default="etl_config.toml", help="Config file in TOML format.")
def main(config):

    pipeline(config)


if __name__ == "__main__":
    main()
