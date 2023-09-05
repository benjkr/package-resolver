import typer
from typing_extensions import Annotated

verbose_param = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Run on verbose mode",
        show_default=True,
    ),
]

output_dir_param = Annotated[
    str,
    typer.Option(
        "--output-dir",
        "-o",
        help="Output directory",
        show_default=True,
    ),
]

no_cleanup_param = Annotated[
    bool,
    typer.Option(
        "--no-cleanup",
        "-c",
        help="No cleanup after finished",
        show_default=True,
    ),
]

package_param = Annotated[str, typer.Argument(..., help="Package to download")]
