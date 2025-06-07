## Overview

This Python script provides an automated, interactive workflow for analyzing microbiome data using QIIME2. The script guides users through a complete analysis pipeline from raw sequence data to publication-ready visualizations and exportable data formats, with built-in file existence checks to enable efficient reruns.

## Features

- **Interactive Workflow**: Guides users through each step with clear prompts and explanations
- **Smart Rerun Capability**: Checks for existing output files and skips completed steps
- **Visual Progress Indicators**: Animated spinner shows when commands are running
- **Customizable Parameters**: Allows adjustment of key parameters like primer sequences and truncation lengths
- **Comprehensive Pipeline**: Covers the entire analysis from raw sequences to diversity metrics and taxonomic classification
- **Automatic Visualization**: Opens QIIME2 visualizations in a web browser
- **Data Export**: Exports QIIME2 artifacts to standard formats for downstream analysis

## Prerequisites

Before running the script, ensure you have:

1. QIIME2 installed and activated in your environment
2. A directory named `paired-end-demultiplexed` containing your demultiplexed FASTQ files
3. A `metadata.tsv` file with your sample metadata
4. A `classifier.qza` file for taxonomic classification

## Pipeline Steps

The script performs the following analysis steps:

### 1. Sequence Import
Imports paired-end demultiplexed sequences into QIIME2 format.

```
qiime tools import \
--type 'SampleData[PairedEndSequencesWithQuality]' \
--input-path paired-end-demultiplexed \
--input-format CasavaOneEightSingleLanePerSampleDirFmt \
--output-path demux-paired-end.qza
```

### 2. Demultiplexed Data Summarization
Generates quality plots to assess sequence quality.

```
qiime demux summarize \
--i-data demux-paired-end.qza \
--o-visualization demux-paired-end-summ.qzv
```

### 3. Adapter Trimming with Cutadapt
Removes primer sequences from reads. Default primers are for the V3-V4 region, but custom primers can be specified.

```
qiime cutadapt trim-paired \
--i-demultiplexed-sequences demux-paired-end.qza \
--p-front-f CCTACGGGNGGCWGCAG \
--p-front-r GACTACHVGGGTATCTAATCC \
--o-trimmed-sequences trim-seqs.qza
```

### 4. DADA2 Denoising
Performs quality filtering, denoising, merging of paired reads, and chimera removal. Parameters can be customized based on quality plots.

```
qiime dada2 denoise-paired \
--i-demultiplexed-seqs trim-seqs.qza \
--p-trim-left-f 0 \
--p-trim-left-r 0 \
--p-trunc-len-f 250 \
--p-trunc-len-r 250 \
--o-table dada-table.qza \
--o-representative-sequences dada-rep-seqs.qza \
--o-denoising-stats dada-denoising-stats.qza
```

### 5. Feature Table and Sequence Summarization
Summarizes the feature table and representative sequences.

```
qiime feature-table summarize \
--i-table dada-table.qza \
--o-visualization dada-table-summ.qzv \
--m-sample-metadata-file metadata.tsv

qiime feature-table tabulate-seqs \
--i-data dada-rep-seqs.qza \
--o-visualization dada-rep-seqs-summ.qzv
```

### 6. Multiple Sequence Alignment with MAFFT
Aligns representative sequences.

```
qiime alignment mafft \
--i-sequences dada-rep-seqs.qza \
--o-alignment dada-aligned-seqs.qza
```

### 7. Alignment Masking
Masks highly variable positions in the alignment.

```
qiime alignment mask \
--i-alignment dada-aligned-seqs.qza \
--o-masked-alignment dada-masked-aligned-seqs.qza
```

### 8. Phylogenetic Tree Construction with FastTree
Builds a phylogenetic tree from the aligned sequences.

```
qiime phylogeny fasttree \
--i-alignment dada-masked-aligned-seqs.qza \
--o-tree dada-unrooted-tree.qza
```

### 9. Tree Rooting
Creates a rooted phylogenetic tree.

```
qiime phylogeny midpoint-root \
--i-tree dada-unrooted-tree.qza \
--o-rooted-tree dada-rooted-tree.qza
```

### 10. Alpha Rarefaction Analysis
Generates rarefaction curves to determine appropriate sampling depth.

```
qiime diversity alpha-rarefaction \
--i-table dada-table.qza \
--i-phylogeny dada-rooted-tree.qza \
--p-max-depth {max_depth} \
--m-metadata-file metadata.tsv \
--o-visualization alpha-rarefaction.qzv
```

### 11. Taxonomic Classification
Classifies sequences using a pre-trained classifier.

```
qiime feature-classifier classify-sklearn \
--i-classifier classifier.qza \
--i-reads dada-rep-seqs.qza \
--o-classification taxonomy.qza
```

### 12. Taxonomy Visualization
Generates a visualization of the taxonomic classifications.

```
qiime metadata tabulate \
--m-input-file taxonomy.qza \
--o-visualization taxonomy-summ.qzv
```

### 13. Feature Table Filtering
Filters the feature table to remove features with low frequency.

```
qiime feature-table filter-features \
--i-table dada-table.qza \
--p-min-frequency 10 \
--o-filtered-table dada-filtered-table.qza
```

### 14. Mitochondria and Chloroplast Filtering
Removes mitochondrial and chloroplast sequences.

```
qiime taxa filter-table \
--i-table dada-filtered-table.qza \
--i-taxonomy taxonomy.qza \
--p-exclude mitochondria,chloroplast \
--o-filtered-table dada-filtered-nmnc-table.qza
```

### 15. Taxonomy Collapsing to Genus Level
Collapses the feature table to genus level.

```
qiime taxa collapse \
--i-table dada-filtered-nmnc-table.qza \
--i-taxonomy taxonomy.qza \
--p-level 6 \
--o-collapsed-table dada-filtered-nmnc-table-l6.qza
```

### 16. Collapsed Table Summarization
Summarizes the collapsed feature table.

```
qiime feature-table summarize \
--i-table dada-filtered-nmnc-table-l6.qza \
--o-visualization dada-filtered-nmnc-table-l6-summ.qzv \
--m-sample-metadata-file metadata.tsv
```

### 17. Taxa Barplots
Generates barplots to visualize taxonomic composition.

```
qiime taxa barplot \
--i-table dada-filtered-nmnc-table.qza \
--i-taxonomy taxonomy.qza \
--m-metadata-file metadata.tsv \
--o-visualization taxa-bar-plots.qzv
```

### 18. Core Metrics Phylogenetic Analysis
Calculates alpha and beta diversity metrics.

```
qiime diversity core-metrics-phylogenetic \
--i-phylogeny dada-rooted-tree.qza \
--i-table dada-filtered-nmnc-table.qza \
--p-sampling-depth {sampling_depth} \
--m-metadata-file metadata.tsv \
--output-dir metrics
```

### 19. Export to Standard Formats
Exports QIIME2 artifacts to standard formats for downstream analysis:

- Feature table to BIOM and TSV formats
- Taxonomy assignments to TSV
- Representative sequences to FASTA
- Phylogenetic tree to Newick format
- Alpha diversity metrics to TSV
- Beta diversity distance matrices to TSV
- Collapsed taxonomic tables to BIOM and TSV

## Usage

1. Ensure QIIME2 is activated in your environment
2. Place your input files in the appropriate locations
3. Run the script: `python grigsby_qiime2_script.py`
4. Follow the interactive prompts to complete the analysis

## Rerunning the Analysis

If you need to rerun the analysis, simply execute the script again. It will:
1. Check for existing output files at each step
2. Skip steps that have already been completed
3. Prompt you to view existing visualizations
4. Continue from where you left off

This makes it efficient to:
- Resume interrupted analyses
- Update parameters for specific steps without redoing the entire pipeline
- Quickly generate new visualizations from existing data

## Customization

The script allows customization of several key parameters:
- Primer sequences for adapter trimming
- DADA2 truncation parameters for quality filtering
- Sampling depth for diversity analyses
- Alpha rarefaction maximum depth

## Output Files

The script generates numerous output files:
- `.qza` files: QIIME2 artifacts containing analysis data
- `.qzv` files: QIIME2 visualizations viewable in a web browser
- Exported files in the `exports` directory in standard formats

## Troubleshooting

If you encounter issues with QIIME2 visualizations not loading correctly:
1. Manually drag and drop the `.qzv` file onto https://view.qiime2.org
2. Use the QIIME2 command line: `qiime tools view file.qzv`

## Dependencies

- Python 3.6+
- QIIME2 (2019.10 or later)
- Required QIIME2 plugins:
  - cutadapt
  - dada2
  - feature-table
  - alignment
  - phylogeny
  - diversity
  - feature-classifier
  - taxa

## Citation

If you use this script in your research, please cite:
- QIIME2: Bolyen E, et al. (2019). Reproducible, interactive, scalable and extensible microbiome data science using QIIME 2. Nature Biotechnology.
- This script: [Your citation information]

## License

This script is provided under the MIT License. See the LICENSE file for details.
