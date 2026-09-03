#!/bin/bash
for s in 01_check_dataset 02_group_mean 03_group_sd 06_vertexwise_icc \
         07_icc_histogram 08_export_statistics 09_group_tmaps \
         10_threshold_group_tmaps 11_group_tmap_correlation 12_dice_coefficient \
         13_whole_map_similarity 14_rank_order_continuity \
         15_whole_map_similarity_histogram 16_rank_order_scatter \
         17_group_tmap_scatter 18_group_mean_correlation 20_check_yeo_labels \
         21_network_summary_scores 22_network_rank_order_continuity \
         23_network_vertexwise_icc 25_criticality_overlap_chance \
         26_qc_yeo_mapping 27_qc_reliability 28_network_icc_qc 29_test_icc_ci \
         30_check_data_completeness 31_demeaned_whole_map_similarity \
         32_group_mean_scatter 33_render_surfaces; do
  echo "=== Running $s ==="
  python -m scripts.$s || echo "!!! FAILED: $s !!!"
done
