# Xmmvec

Interactive Visualization tool to explore for the values and ranks of the values 
in a mmvec (or other) matrix of numbers, using selections based on these values 
and ranks as well as metadata associated with the features in row and/or columns 
of the matrix.

## Installation

For the first install:
```
pip install git+https://github.com/FranckLejzerowicz/Xmmvec.git
```

and then if there are updates...
```
pip install --upgrade git+https://github.com/FranckLejzerowicz/Xmmvec.git
```

*_Note that python and pip should be python3_

## Input

* Data files:
  - `-r, --i-ranks-path`: mmvec output matrix of conditional probabilities between the omic1 
features and omic2 features

* Output:
  - `-o, --o-ranks-explored` (optional): Xmmvec visualization output (must end with be .html)  

* Metadata:
  - `-m1, --p-omic1-metadata` and `-m1, --p-omic1-metadata` (optional): feature metadata tables 
  for 'omic1' and 'omic2' features. Must contains the passed columns (next option) or ignored.
  - `-c1, --p-omic1-column` and `-c2, --p-omic2-column` (optional): columns of the respective
  metadata tables to use for features coloring.
  - `-n1, --p-omic1-name` and `-n2, --p-omic2-name` (optional): names to identify the 'omic1' 
  and 'omic2' features (and label the interactive selectors). This is invented and maz not match
  the data (e.g. "*myGenomes*" would work). 

* Filtering (based on metadata):
  - `-f1, --p-omic1-filt` and `-f2, --p-omic2-filt` (optional): column of the 'omic1' (and/or 'omic2') 
  features metadata table passed to `-m1, --p-omic1-metadata` (and/or `-m2, --p-omic2-metadata`) that  
  is used for features filtering.  
  - `-v1, --p-omic1-value` and `-v2, --p-omic2-value` (optional): factor(s) (or threshold(s)) for columns
  `-f1, --p-omic1-filt` (and/or `-f2, --p-omic2-filt`) used to filter the features.

The names of the paired omics can be invented (using `-n1` and `-n2`), 
but note that the features in:
  - the columns of the matrix will be associated with options `1` (`-m1`, `-c1`, `-n1`, `-f1`, `-v1`).
  - the rows of the matrix will be associated with options `2` (`-m2`, `-c2`, `-n2`, `-f2`, `-v2`).

## Outputs

A vizualization file in html containing three interactive panels:
1. a heatmap of conditional probability values (or ranked values upon selection)
2. a barplot for the features of 'omic1' average probabilities: there to use shift + click bars to highlight features 
2. a barplot for the features of 'omic2' average probabilities (same functionality). 

(hover over the heatmap cells or bars to get additional information)

#### Sliders

The sliders allows one to only show on the heatmap the co-occurrences probabilities that for each\
feature are the most highly ranked (i.e. setting a slider to 10 would subset to the top 10 
co-occurring features of an axis for each feature on the other axis):
- The first slider controls the co-occurring features of omic1 for each feature of omic2.   
- The second slider controls the co-occurring features of omic2 for each feature of omic1.   

#### Selectors

On the very bottom, there are four selectors under label `Conditional_conditional`. This is to 
toggle the data in the heatmap in terms of:
- `conditionals`: raw conditional probability values.
- `ranked_conditionals`: raw conditional probability values ranked from the smallest to the 
largest (i.e. across the board).
- `conditionals_per_<omic1>`: conditional probability values ranked separately for each feature 
of *omic1*, from the least to the most probably co-occurring features of *omic2*.     
- `conditionals_per_<omic2>`: conditional probability values ranked separately for each feature 
of *omic2*, from the least to the most probably co-occurring features of *omic1*.     


## Example

If no output file name is specified, the input filename is stripped from its extension,
which is replaced by the values of options `-p, --p-min-probability` and `-n, --p-pair-number`,
and the `.html` extension.

- Running:

    ```
    Xmmvec \
        -r Xmmvec/tests/example/ranks.tsv \
        -p 1 \
        -n 100 \
        -n1 omic1 \
        -n2 omic2 \
        -m1 meta_omic1.tsv \
        -m1 meta_omic2.tsv \
        -c1 Taxolevel_B \
        -c2 Taxolevel_C \
    ```
    Would return file `Xmmvec/tests/example/ranks-p1-n100.html` with 'omic1' and 'omic2' as 
    columns and rows in the interactive heatmap coloured per values.


### Optional arguments

```
  -r, --i-ranks-path TEXT         Path to mmvec ranks.  [required]
  -o, --o-ranks-explored TEXT     Path to the output explorer visualization.
  -t, --i-tree-taxonomy TEXT      Path to a tree which internal nodes are
                                  labeled.

  -m1, --p-omic1-metadata TEXT    {Path to the metadata table for omic1
                                  features (columns of the ranks matrix).

  -c1, --p-omic1-column TEXT      Column from metadata to use for
                                  stratification of omic1 features.

  -f1, --p-omic1-filt TEXT        Column from metadata `-m1` to use for
                                  filtering based on values of `-f1`.

  -v1, --p-omic1-value TEXT       Filter omic1 features based on column passed
                                  to `-f1`.

  -n1, --p-omic1-name TEXT        Name for omic1 features.  [default: omic1]
  -m2, --p-omic2-metadata TEXT    {Path to the metadata table for omic2
                                  features (rows of the ranks matrix).

  -c2, --p-omic2-column TEXT      Column from metadata to use for
                                  stratification of omic2 features.

  -f2, --p-omic2-filt TEXT        Column from metadata `-m2` to use for
                                  filtering based on values of `-f2`.

  -v2, --p-omic2-value TEXT       Filter omic2 features based on column passed
                                  to `-f2`.

  -n2, --p-omic2-name TEXT        Name for omic2 features.  [default: omic2]
  -p, --p-min-probability FLOAT   Minimum conditional probability.  [default:
                                  0.0]

  -n, --p-pair-number INTEGER     initial number of co-occurrences per
                                  feature.  [default: 10]

  -col, --p-color-palette [blues|greens|oranges|reds|purples|greys|viridis|magma|inferno|plasma|bluegreen|bluepurple|greenblue|orangered|purplebluegreen|purpleblue|purplered|redpurple|yellowgreenblue|yellowgreen|yelloworangebrown|yelloworangered|blueorange|brownbluegreen|purplegreen|pinkyellowgreen|purpleorange|redblue|redgrey|redyellowblue|redyellowgreen|spectral|rainbow|sinebow]
                                  Color palette for the heatmap.  [default:
                                  rainbow]

  --version                       Show the version and exit.
  --help                          Show this message and exit.
```



### Bug Reports

contact `flejzerowicz@health.ucsd.edu`