#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import webbrowser
import threading
import itertools

def display_logo():
    """Display the GRIGSBY QIIME2 SCRIPT ASCII art logo"""
    logo = r"""
      ___                                   ___           ___         
     /\  \          ___         ___        /\__\         /\  \          
    /::\  \        /\  \       /\  \      /::|  |       /::\  \      
   /:/\:\  \       \:\  \      \:\  \    /:|:|  |      /:/\:\  \         
   \:\~\:\  \      /::\__\     /::\__\  /:/|:|__|__   /::\~\:\  \      
    \:\ \:\__\  __/:/\/__/  __/:/\/__/ /:/ |::::\__\ /:/\:\ \:\__\   
     \:\/:/  / /\/:/  /    /\/:/  /    \/__/~~/:/  / \:\~\:\ \/__/   
      \::/  /  \::/__/     \::/__/           /:/  /   \:\ \:\__\     
      /:/  /    \:\__\      \:\__\          /:/  /     \:\ \/__/    
     /:/  /      \/__/       \/__/         /:/  /       \:\__\         
     \/__/                                 \/__/         \/__/  

      ___                       ___           ___     
     /\  \          ___        /\__\         /\  \    
     \:\  \        /\  \      /::|  |       /::\  \   
      \:\  \       \:\  \    /:|:|  |      /:/\:\  \  
      /::\  \      /::\__\  /:/|:|__|__   /::\~\:\  \ 
     /:/\:\__\  __/:/\/__/ /:/ |::::\__\ /:/\:\ \:\__\
    /:/  \/__/ /\/:/  /    \/__/~~/:/  / \:\~\:\ \/__/
   /:/  /      \::/__/           /:/  /   \:\ \:\__\  
   \/__/        \:\__\          /:/  /     \:\ \/__/  
                 \/__/         /:/  /       \:\__\    
                               \/__/         \/__/       
 _  __             _                                   _  
/ |/ /_  ___    __| | ___ _ __ ___  _   ___  _____  __| | 
| | '_ \/ __|  / _` |/ _ \ '_ ` _ \| | | \ \/ / _ \/ _` | 
| | (_) \__ \ | (_| |  __/ | | | | | |_| |>  <  __/ (_| | 
|_|\___/|___/  \__,_|\___|_| |_| |_|\__,_/_/\_\___|\__,_| 
                                                          
             _              _                      _      
 _ __   __ _(_)_ __ ___  __| |       ___ _ __   __| |___  
| '_ \ / _` | | '__/ _ \/ _` |_____ / _ \ '_ \ / _` / __| 
| |_) | (_| | | | |  __/ (_| |_____|  __/ | | | (_| \__ \ 
| .__/ \__,_|_|_|  \___|\__,_|      \___|_| |_|\__,_|___/ 
|_|                                                       
    """
    print(logo)
    print("\n" + "=" * 80)
    print("Welcome to my QIIME2 Analysis Pipeline, made for use with version 2025.4".center(80))
    print("=" * 80 + "\n")

def fly_message(message, type="info"):
    """Display a message with emoji indicators, fly emoji only for step headers"""
    # Only show the fly emoji for step headers (messages that start with '=====')
    has_fly = message.startswith("\n=====")
    
    if type == "info":
        print(f"{('🪰 ' if has_fly else '')}{message}")
    elif type == "success":
        print(f"{'🪰' if has_fly else ''}✅ SUCCESS: {message}")
    elif type == "running":
        print(f"Running: {message}")
    elif type == "warning":
        print(f"⚠ WARNING: {message}")
    elif type == "error":
        print(f"❌ ERROR: {message}")
    elif type == "input":
        print(f"❓ {message}")
    elif type == "skip":
        print(f"⏩ SKIPPING: {message} (files already exist)")
    sys.stdout.flush()  # Ensure message is displayed immediately

def check_output_exists(files):
    """Check if all output files already exist"""
    if isinstance(files, str):
        files = [files]
    return all(os.path.exists(f) for f in files)

def spinner_animation(stop_event, description):
    """Display an animated spinner while a command is running"""
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(f"\r🪰 Running: {description}... {next(spinner)} ")
        sys.stdout.flush()
        time.sleep(0.1)
    # Clear the spinner line when done
    sys.stdout.write(f"\r{' ' * (len(description) + 20)}\r")
    sys.stdout.flush()

def run_command(command, description):
    """Run a command with error handling and animated spinner"""
    fly_message(f"Running: {description}...", "running")
    
    # Set up and start the spinner in a separate thread
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_animation, args=(stop_spinner, description))
    spinner_thread.daemon = True
    spinner_thread.start()
    
    try:
        result = subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, text=True)
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        fly_message(f"Successfully completed: {description}", "success")
        return True
    except subprocess.CalledProcessError as e:
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        fly_message(f"ERROR: Command failed: {e.cmd}", "error")
        fly_message(f"ERROR: Error details: {e.stderr}", "error")
        return False

def open_qzv_file(file_path):
    """Open the default QIIME2 View site for manual file loading"""
    if os.path.exists(file_path):
        fly_message(f"Opening QIIME2 View site for {file_path}...")
        webbrowser.open("https://view.qiime2.org")
        
        # Provide instructions for manual file loading
        print("\n" + "-" * 80)
        fly_message(f"To view {file_path}, please:", "info")
        fly_message(f"1. Drag and drop {file_path} onto the QIIME2 View site that just opened", "info")
        fly_message(f"2. Or use the 'Choose File' button on the QIIME2 View site", "info")
        fly_message(f"File path: {os.path.abspath(file_path)}", "info")
        print("-" * 80 + "\n")
    else:
        fly_message(f"Could not find {file_path} to open", "warning")

def check_prerequisites():
    """Check if all required files and directories exist"""
    fly_message("Checking for required files and directories...", "info")
    
    # Check for paired-end-demultiplexed directory
    if not os.path.isdir("paired-end-demultiplexed"):
        fly_message("Missing 'paired-end-demultiplexed' directory with FASTQ files!", "error")
        return False
    
    # Check for metadata.tsv
    if not os.path.isfile("metadata.tsv"):
        fly_message("Missing 'metadata.tsv' file!", "error")
        return False
    
    # Check for classifier.qza
    if not os.path.isfile("classifier.qza"):
        fly_message("Missing 'classifier.qza' file!", "error")
        return False
    
    fly_message("All required files are present!", "success")
    return True

def main():
    """Main function to run the QIIME2 workflow"""
    display_logo()
    
    fly_message("This script will guide you through a complete QIIME2 analysis workflow", "info")
    
    # Check prerequisites
    fly_message("Before we begin, let's check if you have all the required files:", "info")
    fly_message("1. 'paired-end-demultiplexed' folder with FASTQ files", "info")
    fly_message("2. 'metadata.tsv' file with sample metadata", "info")
    fly_message("3. 'classifier.qza' for taxonomic classification", "info")
    
    if not check_prerequisites():
        fly_message("Please add the missing files and run the script again", "error")
        return
    
    # Step 1: Import sequences
    fly_message("\n===== STEP 1: IMPORTING SEQUENCES =====", "info")
    if check_output_exists("demux-paired-end.qza"):
        fly_message("Sequence import", "skip")
    elif not run_command(
        "qiime tools import \
        --type 'SampleData[PairedEndSequencesWithQuality]' \
        --input-path paired-end-demultiplexed \
        --input-format CasavaOneEightSingleLanePerSampleDirFmt \
        --output-path demux-paired-end.qza",
        "Sequence import"
    ):
        fly_message("Failed to import sequences. Exiting...", "error")
        return
    
    # Step 2: Summarize demultiplexed data
    fly_message("\n===== STEP 2: SUMMARIZING DEMULTIPLEXED DATA =====", "info")
    if check_output_exists("demux-paired-end-summ.qzv"):
        fly_message("Demultiplexed data summarization", "skip")
    elif not run_command(
        "qiime demux summarize \
        --i-data demux-paired-end.qza \
        --o-visualization demux-paired-end-summ.qzv",
        "Demux summarization"
    ):
        fly_message("Failed to summarize demultiplexed data. Exiting...", "error")
        return
    else:
        open_qzv_file("demux-paired-end-summ.qzv")
    
    # Prompt to examine quality plots
    fly_message("Please examine the sequence quality plots to determine appropriate trimming parameters", "input")
    input("Press Enter to continue once you've reviewed the quality plots...")
    
    # Step 3: Trim adapters with cutadapt
    fly_message("\n===== STEP 3: TRIMMING ADAPTERS WITH CUTADAPT =====", "info")
    fly_message("Default primers are:", "info")
    fly_message("Forward (V3-V4 region): CCTACGGGNGGCWGCAG", "info")
    fly_message("Reverse (V3-V4 region): GACTACHVGGGTATCTAATCC", "info")
    
    use_custom_primers = input("🪰❓ Do you want to use custom primers? (yes/no): ").strip().lower()
    
    if use_custom_primers == "yes" or use_custom_primers == "y":
        forward_primer = input("🪰❓ Enter your forward primer sequence: ").strip()
        reverse_primer = input("🪰❓ Enter your reverse primer sequence: ").strip()
        fly_message(f"Using custom primers - Forward: {forward_primer}, Reverse: {reverse_primer}", "info")
    else:
        forward_primer = "CCTACGGGNGGCWGCAG"  # Default V3-V4 region forward primer
        reverse_primer = "GACTACHVGGGTATCTAATCC"  # Default V3-V4 region reverse primer
        fly_message("Using default V3-V4 region primers", "info")
    
    if check_output_exists("trim-seqs.qza"):
        fly_message("Adapter trimming", "skip")
    elif not run_command(
        f"qiime cutadapt trim-paired \
        --i-demultiplexed-sequences demux-paired-end.qza \
        --p-front-f {forward_primer} \
        --p-front-r {reverse_primer} \
        --o-trimmed-sequences trim-seqs.qza",
        "Adapter trimming"
    ):
        fly_message("Failed to trim adapters. Exiting...", "error")
        return
    
    # Step 4: DADA2 denoising
    fly_message("\n===== STEP 4: DADA2 DENOISING =====", "info")
    fly_message("Default DADA2 parameters are:", "info")
    fly_message("Trim left (forward): 0", "info")
    fly_message("Trim left (reverse): 0", "info")
    fly_message("Truncation length (forward): 250", "info")
    fly_message("Truncation length (reverse): 250", "info")
    fly_message("These values determine how much of each read to keep. Adjust based on quality plots.", "info")
    
    use_custom_trunc = input("❓ Do you want to customize DADA2 truncation parameters? (yes/no): ").strip().lower()
    
    if use_custom_trunc == "yes" or use_custom_trunc == "y":
        trim_left_f = input("❓ Enter trim-left-f value (bases to remove from start of forward reads): ").strip()
        trim_left_r = input("❓ Enter trim-left-r value (bases to remove from start of reverse reads): ").strip()
        trunc_len_f = input("❓ Enter trunc-len-f value (length to truncate forward reads): ").strip()
        trunc_len_r = input("❓ Enter trunc-len-r value (length to truncate reverse reads): ").strip()
        fly_message(f"Using custom truncation parameters - trim-left-f: {trim_left_f}, trim-left-r: {trim_left_r}, trunc-len-f: {trunc_len_f}, trunc-len-r: {trunc_len_r}", "info")
    else:
        trim_left_f = "0"  # Default trim-left-f
        trim_left_r = "0"  # Default trim-left-r
        trunc_len_f = "250"  # Default trunc-len-f
        trunc_len_r = "250"  # Default trunc-len-r
        fly_message("Using default truncation parameters", "info")
    
    fly_message("This step may take a while... Time to stretch your wings!", "info")
    # Check if DADA2 outputs already exist
    if check_output_exists(["dada-table.qza", "dada-rep-seqs.qza", "dada-denoising-stats.qza"]):
        fly_message("DADA2 denoising", "skip")
    else:
        # Use the QIIME2 CLI command for DADA2 with customizable parameters
        if not run_command(
            f"qiime dada2 denoise-paired \
            --i-demultiplexed-seqs trim-seqs.qza \
            --p-trim-left-f {trim_left_f} \
            --p-trim-left-r {trim_left_r} \
            --p-trunc-len-f {trunc_len_f} \
            --p-trunc-len-r {trunc_len_r} \
            --o-table dada-table.qza \
            --o-representative-sequences dada-rep-seqs.qza \
            --o-denoising-stats dada-denoising-stats.qza",
            "DADA2 denoising"
        ):
            fly_message("Failed to denoise sequences. Exiting...", "error")
            return
    
    # Step 5: View denoising stats
    fly_message("\n===== STEP 5: VIEWING DENOISING STATISTICS =====", "info")
    if check_output_exists("dada-denoising-stats-summ.qzv"):
        fly_message("Denoising stats tabulation", "skip")
        if input("🪰❓ Would you like to view the denoising stats? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("dada-denoising-stats-summ.qzv")
    elif not run_command(
        "qiime metadata tabulate \
        --m-input-file dada-denoising-stats.qza \
        --o-visualization dada-denoising-stats-summ.qzv",
        "Denoising stats tabulation"
    ):
        fly_message("Failed to tabulate denoising stats. Continuing anyway...", "warning")
    else:
        open_qzv_file("dada-denoising-stats-summ.qzv")
    
    # Step 6: Tabulate representative sequences
    fly_message("\n===== STEP 6: TABULATING REPRESENTATIVE SEQUENCES =====", "info")
    if check_output_exists("dada-rep-seqs-summ.qzv"):
        fly_message("Representative sequences tabulation", "skip")
        if input("🪰❓ Would you like to view the representative sequences? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("dada-rep-seqs-summ.qzv")
    elif not run_command(
        "qiime feature-table tabulate-seqs \
        --i-data dada-rep-seqs.qza \
        --o-visualization dada-rep-seqs-summ.qzv",
        "Representative sequences tabulation"
    ):
        fly_message("Failed to tabulate representative sequences. Continuing anyway...", "warning")
    else:
        open_qzv_file("dada-rep-seqs-summ.qzv")
    
    # Step 7: Summarize feature table
    fly_message("\n===== STEP 7: SUMMARIZING FEATURE TABLE =====", "info")
    if check_output_exists("dada-table-summ.qzv"):
        fly_message("Feature table summarization", "skip")
        if input("🪰❓ Would you like to view the feature table summary? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("dada-table-summ.qzv")
    elif not run_command(
        "qiime feature-table summarize \
        --i-table dada-table.qza \
        --o-visualization dada-table-summ.qzv \
        --m-sample-metadata-file metadata.tsv",
        "Feature table summarization"
    ):
        fly_message("Failed to summarize feature table. Continuing anyway...", "warning")
    else:
        open_qzv_file("dada-table-summ.qzv")
    
    # Step 8: Sequence alignment with MAFFT
    fly_message("\n===== STEP 8: ALIGNING SEQUENCES WITH MAFFT =====", "info")
    if check_output_exists("dada-rep-seqs-alligned.qza"):
        fly_message("MAFFT alignment", "skip")
    elif not run_command(
        "qiime alignment mafft \
        --i-sequences dada-rep-seqs.qza \
        --o-alignment dada-rep-seqs-alligned.qza",
        "MAFFT alignment"
    ):
        fly_message("Failed to align sequences. Exiting...", "error")
        return
    
    # Step 9: Mask alignment
    fly_message("\n===== STEP 9: MASKING ALIGNMENT =====", "info")
    if check_output_exists("dada-rep-seqs-alligned-masked.qza"):
        fly_message("Alignment masking", "skip")
    elif not run_command(
        "qiime alignment mask \
        --i-alignment dada-rep-seqs-alligned.qza \
        --o-masked-alignment dada-rep-seqs-alligned-masked.qza",
        "Alignment masking"
    ):
        fly_message("Failed to mask alignment. Exiting...", "error")
        return
    
    # Step 10: Build phylogenetic tree with FastTree
    fly_message("\n===== STEP 10: BUILDING PHYLOGENETIC TREE WITH FASTTREE =====", "info")
    if check_output_exists("dada-unrooted-tree.qza"):
        fly_message("FastTree phylogeny construction", "skip")
    elif not run_command(
        "qiime phylogeny fasttree \
        --i-alignment dada-rep-seqs-alligned-masked.qza \
        --o-tree dada-unrooted-tree.qza",
        "FastTree phylogeny construction"
    ):
        fly_message("Failed to build phylogenetic tree. Exiting...", "error")
        return
    
    # Step 11: Root the tree
    fly_message("\n===== STEP 11: ROOTING THE PHYLOGENETIC TREE =====", "info")
    if check_output_exists("dada-rooted-tree.qza"):
        fly_message("Tree rooting", "skip")
    elif not run_command(
        "qiime phylogeny midpoint-root \
        --i-tree dada-unrooted-tree.qza \
        --o-rooted-tree dada-rooted-tree.qza",
        "Tree rooting"
    ):
        fly_message("Failed to root the tree. Exiting...", "error")
        return
    
    # Step 12: Alpha rarefaction
    fly_message("\n===== STEP 12: ALPHA RAREFACTION ANALYSIS =====", "info")
    
    if check_output_exists("alpha-rarefaction.qzv"):
        fly_message("Alpha rarefaction analysis", "skip")
        if input("🪰❓ Would you like to view the existing alpha rarefaction plot? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("alpha-rarefaction.qzv")
        max_depth = input("🪰❓ Enter the maximum rarefaction depth you determined from the plot: ")
    else:
        fly_message("We need to determine a rarefaction depth for diversity analyses", "input")
        fly_message("Let's generate a rarefaction curve to help with this decision", "info")
        
        # Ask for max depth for rarefaction curve
        max_depth = input("🪰❓ Enter maximum rarefaction depth (suggested: check dada-table-summ.qzv for guidance): ")
        
        if not run_command(
            f"qiime diversity alpha-rarefaction \
            --i-table dada-table.qza \
            --i-phylogeny dada-rooted-tree.qza \
            --p-max-depth {max_depth} \
            --m-metadata-file metadata.tsv \
            --o-visualization alpha-rarefaction.qzv",
            "Alpha rarefaction analysis"
        ):
            fly_message("Failed to perform alpha rarefaction. Exiting...", "error")
            return
        else:
            open_qzv_file("alpha-rarefaction.qzv")
    
    fly_message("Please examine the rarefaction curves to determine an appropriate sampling depth", "input")
    fly_message("Look for the plateau in the curves and choose a depth that retains most samples", "info")
    input("Press Enter to continue once you've reviewed the rarefaction curves...")
    
    # Step 13: Taxonomic classification
    fly_message("\n===== STEP 13: TAXONOMIC CLASSIFICATION =====", "info")
    fly_message("This step may take a while... Flies are patient creatures!", "info")
    if check_output_exists("taxonomy.qza"):
        fly_message("Taxonomic classification", "skip")
    elif not run_command(
        "qiime feature-classifier classify-sklearn \
        --i-classifier classifier.qza \
        --i-reads dada-rep-seqs.qza \
        --o-classification taxonomy.qza",
        "Taxonomic classification"
    ):
        fly_message("Failed to classify taxonomy. Exiting...", "error")
        return
    
    # Step 14: Visualize taxonomy
    fly_message("\n===== STEP 14: VISUALIZING TAXONOMY =====", "info")
    if check_output_exists("taxonomy.qzv"):
        fly_message("Taxonomy visualization", "skip")
        if input("🪰❓ Would you like to view the taxonomy visualization? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("taxonomy.qzv")
    elif not run_command(
        "qiime metadata tabulate \
        --m-input-file taxonomy.qza \
        --o-visualization taxonomy.qzv",
        "Taxonomy visualization"
    ):
        fly_message("Failed to visualize taxonomy. Continuing anyway...", "warning")
    else:
        open_qzv_file("taxonomy.qzv")
    
    # Step 15: Filter feature table
    fly_message("\n===== STEP 15: FILTERING FEATURE TABLE =====", "info")
    if check_output_exists("dada-filtered-table.qza"):
        fly_message("Feature table filtering", "skip")
    elif not run_command(
        "qiime feature-table filter-features \
        --i-table dada-table.qza \
        --p-min-samples 2 \
        --o-filtered-table dada-filtered-table.qza",
        "Feature table filtering"
    ):
        fly_message("Failed to filter feature table. Exiting...", "error")
        return
    
    # Step 16: Filter out mitochondria and chloroplast
    fly_message("\n===== STEP 16: FILTERING MITOCHONDRIA AND CHLOROPLAST =====", "info")
    if check_output_exists("dada-filtered-nmnc-table.qza"):
        fly_message("Mitochondria and chloroplast filtering", "skip")
    elif not run_command(
        "qiime taxa filter-table \
        --i-table dada-filtered-table.qza \
        --i-taxonomy taxonomy.qza \
        --p-exclude mitochondria,chloroplast \
        --o-filtered-table dada-filtered-nmnc-table.qza",
        "Mitochondria and chloroplast filtering"
    ):
        fly_message("Failed to filter mitochondria and chloroplast. Exiting...", "error")
        return
    
    # Step 17: Collapse taxonomy to level 6 (genus)
    fly_message("\n===== STEP 17: COLLAPSING TAXONOMY TO GENUS LEVEL =====", "info")
    if check_output_exists("dada-filtered-nmnc-table-l6.qza"):
        fly_message("Taxonomy collapsing", "skip")
    elif not run_command(
        "qiime taxa collapse \
        --i-table dada-filtered-nmnc-table.qza \
        --i-taxonomy taxonomy.qza \
        --p-level 6 \
        --o-collapsed-table dada-filtered-nmnc-table-l6.qza",
        "Taxonomy collapsing"
    ):
        fly_message("Failed to collapse taxonomy. Exiting...", "error")
        return
    
    # Step 18: Summarize collapsed table
    fly_message("\n===== STEP 18: SUMMARIZING COLLAPSED TABLE =====", "info")
    if check_output_exists("dada-filtered-nmnc-table-l6.qzv"):
        fly_message("Collapsed table summarization", "skip")
        if input("🪰❓ Would you like to view the collapsed table visualization? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("dada-filtered-nmnc-table-l6.qzv")
    elif not run_command(
        "qiime feature-table summarize \
        --i-table dada-filtered-nmnc-table-l6.qza \
        --o-visualization dada-filtered-nmnc-table-l6.qzv \
        --m-sample-metadata-file metadata.tsv",
        "Collapsed table summarization"
    ):
        fly_message("Failed to summarize collapsed table. Continuing anyway...", "warning")
    else:
        open_qzv_file("dada-filtered-nmnc-table-l6.qzv")
    
    # Step 19: Generate taxa barplots
    fly_message("\n===== STEP 19: GENERATING TAXONOMY BARPLOTS =====", "info")
    if check_output_exists("taxa-bar-plots.qzv"):
        fly_message("Taxonomy barplot generation", "skip")
        if input("🪰❓ Would you like to view the taxonomy barplots? (yes/no): ").strip().lower() in ["yes", "y"]:
            open_qzv_file("taxa-bar-plots.qzv")
    elif not run_command(
        "qiime taxa barplot \
        --i-table dada-filtered-nmnc-table.qza \
        --i-taxonomy taxonomy.qza \
        --m-metadata-file metadata.tsv \
        --o-visualization taxa-bar-plots.qzv",
        "Taxonomy barplot generation"
    ):
        fly_message("Failed to generate taxonomy barplots. Continuing anyway...", "warning")
    else:
        open_qzv_file("taxa-bar-plots.qzv")
    
    # Step 20: Core metrics phylogenetic analysis
    fly_message("\n===== STEP 20: CORE METRICS PHYLOGENETIC ANALYSIS =====", "info")
    
    metrics_outputs = [
        "metrics/faith_pd_vector.qza", "metrics/observed_features_vector.qza", 
        "metrics/shannon_vector.qza", "metrics/evenness_vector.qza",
        "metrics/unweighted_unifrac_distance_matrix.qza", "metrics/weighted_unifrac_distance_matrix.qza",
        "metrics/jaccard_distance_matrix.qza", "metrics/bray_curtis_distance_matrix.qza"
    ]
    
    if check_output_exists(metrics_outputs):
        fly_message("Core metrics phylogenetic analysis", "skip")
        sampling_depth = input("🪰❓ Enter the sampling depth you previously used for diversity analyses: ")
    else:
        fly_message("Based on your examination of the alpha rarefaction curves, we need to set a sampling depth", "input")
        sampling_depth = input("🪰❓ Enter sampling depth for diversity analyses: ")
        
        if not run_command(
            f"qiime diversity core-metrics-phylogenetic \
            --i-phylogeny dada-rooted-tree.qza \
            --i-table dada-filtered-nmnc-table.qza \
            --p-sampling-depth {sampling_depth} \
            --m-metadata-file metadata.tsv \
            --output-dir metrics",
            "Core metrics phylogenetic analysis"
        ):
            fly_message("Failed to perform core metrics analysis. Exiting...", "error")
            return
    
    # Step 21: Export artifacts to usable formats
    fly_message("\n===== STEP 21: EXPORTING ARTIFACTS TO USABLE FORMATS =====", "info")
    fly_message("Creating 'exports' directory for exported files...", "info")
    
    # Create exports directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")
    
    # Export feature table to biom format
    fly_message("Exporting feature table to biom format...", "info")
    if check_output_exists("exports/feature-table/feature-table.biom"):
        fly_message("Feature table export", "skip")
    elif not run_command(
        "qiime tools export \
        --input-path dada-filtered-nmnc-table.qza \
        --output-path exports/feature-table",
        "Feature table export"
    ):
        fly_message("Failed to export feature table. Continuing anyway...", "warning")
    
    # Convert biom to TSV
    fly_message("Converting feature table from biom to TSV format...", "info")
    if check_output_exists("exports/feature-table/feature-table.tsv"):
        fly_message("Biom to TSV conversion", "skip")
    elif not run_command(
        "biom convert \
        -i exports/feature-table/feature-table.biom \
        -o exports/feature-table/feature-table.tsv \
        --to-tsv",
        "Biom to TSV conversion"
    ):
        fly_message("Failed to convert feature table to TSV. Continuing anyway...", "warning")
    
    # Export taxonomy
    fly_message("Exporting taxonomy assignments...", "info")
    if check_output_exists("exports/taxonomy/taxonomy.tsv"):
        fly_message("Taxonomy export", "skip")
    elif not run_command(
        "qiime tools export \
        --input-path taxonomy.qza \
        --output-path exports/taxonomy",
        "Taxonomy export"
    ):
        fly_message("Failed to export taxonomy. Continuing anyway...", "warning")
    
    # Export representative sequences
    fly_message("Exporting representative sequences...", "info")
    if check_output_exists("exports/rep-seqs/dna-sequences.fasta"):
        fly_message("Representative sequences export", "skip")
    elif not run_command(
        "qiime tools export \
        --input-path dada-rep-seqs.qza \
        --output-path exports/rep-seqs",
        "Representative sequences export"
    ):
        fly_message("Failed to export representative sequences. Continuing anyway...", "warning")
    
    # Export phylogenetic tree
    fly_message("Exporting phylogenetic tree...", "info")
    if check_output_exists("exports/phylogeny/tree.nwk"):
        fly_message("Phylogenetic tree export", "skip")
    elif not run_command(
        "qiime tools export \
        --input-path dada-rooted-tree.qza \
        --output-path exports/phylogeny",
        "Phylogenetic tree export"
    ):
        fly_message("Failed to export phylogenetic tree. Continuing anyway...", "warning")
    
    # Export alpha diversity metrics
    fly_message("Exporting alpha diversity metrics...", "info")
    for metric in ["observed_features", "shannon", "faith_pd", "evenness"]:
        if os.path.exists(f"metrics/{metric}_vector.qza"):
            if check_output_exists(f"exports/alpha-diversity/{metric}/alpha-diversity.tsv"):
                fly_message(f"{metric} export", "skip")
            elif not run_command(
                f"qiime tools export \
                --input-path metrics/{metric}_vector.qza \
                --output-path exports/alpha-diversity/{metric}",
                f"{metric} export"
            ):
                fly_message(f"Failed to export {metric}. Continuing anyway...", "warning")
    
    # Export beta diversity distance matrices
    fly_message("Exporting beta diversity distance matrices...", "info")
    for metric in ["unweighted_unifrac", "weighted_unifrac", "jaccard", "bray_curtis"]:
        if os.path.exists(f"metrics/{metric}_distance_matrix.qza"):
            if check_output_exists(f"exports/beta-diversity/{metric}/distance-matrix.tsv"):
                fly_message(f"{metric} export", "skip")
            elif not run_command(
                f"qiime tools export \
                --input-path metrics/{metric}_distance_matrix.qza \
                --output-path exports/beta-diversity/{metric}",
                f"{metric} export"
            ):
                fly_message(f"Failed to export {metric}. Continuing anyway...", "warning")
    
    # Export collapsed taxonomic table
    fly_message("Exporting collapsed taxonomic table...", "info")
    if check_output_exists("exports/collapsed-table/feature-table.biom"):
        fly_message("Collapsed table export", "skip")
    elif not run_command(
        "qiime tools export \
        --input-path dada-filtered-nmnc-table-l6.qza \
        --output-path exports/collapsed-table",
        "Collapsed table export"
    ):
        fly_message("Failed to export collapsed table. Continuing anyway...", "warning")
    
    # Convert collapsed biom to TSV
    fly_message("Converting collapsed table from biom to TSV format...", "info")
    if check_output_exists("exports/collapsed-table/feature-table-l6.tsv"):
        fly_message("Collapsed biom to TSV conversion", "skip")
    elif not run_command(
        "biom convert \
        -i exports/collapsed-table/feature-table.biom \
        -o exports/collapsed-table/feature-table-l6.tsv \
        --to-tsv",
        "Collapsed biom to TSV conversion"
    ):
        fly_message("Failed to convert collapsed table to TSV. Continuing anyway...", "warning")
    
    fly_message("All artifacts have been exported to the 'exports' directory!", "success")
    
    # Final message
    fly_message("\n===== ANALYSIS COMPLETE =====", "success")
    fly_message("All QIIME2 analysis steps have been completed successfully!", "success")
    fly_message("Output files are available in the current directory, 'metrics' folder, and 'exports' folder", "info")
    fly_message("Thank you for using this QIIME2 Script!", "info")

if __name__ == "__main__":
    main()
