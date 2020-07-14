# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xmmvec.xmmvec import xmmvec
from Xmmvec import __version__


@click.command()
@click.option(
    "-r", "--i-ranks-path", required=True,
    help="Path to mmvec ranks."
)
@click.option(
    "-o", "--o-ranks-explored", required=False,
    help="Path to the output explorer visualization."
)
@click.option(
    "-t", "--i-tree-taxonomy", required=False, default="",
    help="Path to a tree which internal nodes are labeled."
)
@click.option(
    "-m1", "--p-omic1-metadata", required=False, default="",
    show_default=True, help="{Path to the metadata table for omic1 features "
                            "(columns of the ranks matrix)."
)
@click.option(
    "-c1", "--p-omic1-column", required=False, default="",
    show_default=True, help="Column from metadata to use for stratification of omic1 features."
)
@click.option(
    "-n1", "--p-omic1-name", required=False, default="omic1",
    show_default=True, help="Name for omic1 features."
)
@click.option(
    "-m2", "--p-omic2-metadata", required=False, default="",
    show_default=True, help="{Path to the metadata table for omic2 features "
                            "(rows of the ranks matrix)."
)
@click.option(
    "-c2", "--p-omic2-column", required=False, default="",
    show_default=True, help="Column from metadata to use for stratification of omic2 features."
)
@click.option(
    "-n2", "--p-omic2-name", required=False, default="omic2",
    show_default=True, help="Name for omic2 features."
)
@click.option(
    "-p", "--p-min-probability", default=0., show_default=True, type=float,
    help="Minimum conditional probability."
)
@click.option(
    "-n", "--p-pair-number", default=10, show_default=True, type=int,
    help="initial number of co-occurrences per feature."
)
@click.version_option(__version__, prog_name="Xmmvec")


def standalone_xmmvec(
        i_ranks_path,
        o_ranks_explored,
        i_tree_taxonomy,
        p_omic1_metadata,
        p_omic1_column,
        p_omic1_name,
        p_omic2_metadata,
        p_omic2_column,
        p_omic2_name,
        p_min_probability,
        p_pair_number
):

    xmmvec(
        i_ranks_path,
        o_ranks_explored,
        i_tree_taxonomy,
        p_omic1_metadata,
        p_omic1_column,
        p_omic1_name,
        p_omic2_metadata,
        p_omic2_column,
        p_omic2_name,
        p_min_probability,
        p_pair_number
    )


if __name__ == "__main__":
    standalone_xmmvec()
