from flows.non_tech.non_tech_multiagent import generate_test_tasks
import click

cli = click.Group()
cli.add_command(generate_test_tasks)

if __name__ == "__main__":
    cli()
