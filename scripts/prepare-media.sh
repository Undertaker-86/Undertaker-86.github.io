#!/usr/bin/env bash
# Copy, crop and compress portfolio media from the project folders into the site.
# Idempotent: an output is rebuilt only when it is missing or older than its source.
# Run inside the dev shell:  nix develop -c pnpm media     (FORCE=1 rebuilds everything)
#
# Never reads datasets, checkpoints, wandb/, .venv/ or keys: every source below is an explicit file path.
set -euo pipefail

R="${REPO:-$HOME/repository}"
SITE="$(cd "$(dirname "$0")/.." && pwd)"
IMG="$SITE/src/assets"
VID="$SITE/public/media"
LOG="$SITE/scripts/media-sizes.log"
: > "$LOG"

stale() { [[ "${FORCE:-0}" == 1 || ! -e "$2" || "$1" -nt "$2" ]]; }
size() { du -h "$1" | cut -f1; }
note() { printf '%-60s %6s\n' "${1#$SITE/}" "$(size "$1")" | tee -a "$LOG"; }

# img <src> <slug> <name> [maxdim=2000]  → PNG for figures/diagrams, JPEG for photos (by extension of <name>)
img() {
  local src="$1" slug="$2" name="$3" max="${4:-2000}" out="$IMG/$2/$3"
  [[ -f "$src" ]] || { echo "MISSING $src" | tee -a "$LOG"; return 0; }
  mkdir -p "$IMG/$slug"
  if stale "$src" "$out"; then
    case "$name" in
      *.jpg) magick "$src" -auto-orient -resize "${max}x${max}>" -strip -quality 86 -interlace Plane "$out" ;;
      *.png) if [[ "$src" == *.svg ]]; then rsvg-convert -w "$max" -b white "$src" -o "$out";
             else magick "$src" -auto-orient -resize "${max}x${max}>" -strip -define png:compression-level=9 "$out"; fi ;;
    esac
  fi
  note "$out"
}

# vid <src> <slug> <name> <ss> <t> <width> [speed=1] [fps=30] [crf=28] [poster_t=1] [crop filter]
# → <name>.mp4 (H.264), <name>.webm (VP9), poster in src/assets/<slug>/<name>-poster.jpg. Silent, faststart.
vid() {
  local src="$1" slug="$2" name="$3" ss="$4" t="$5" w="$6" sp="${7:-1}" fps="${8:-30}" crf="${9:-28}" pt="${10:-1}" crop="${11:-}"
  [[ -f "$src" ]] || { echo "MISSING $src" | tee -a "$LOG"; return 0; }
  mkdir -p "$VID/$slug" "$IMG/$slug"
  local mp4="$VID/$slug/$name.mp4" webm="$VID/$slug/$name.webm" poster="$IMG/$slug/$name-poster.jpg"
  local vf="${crop:+$crop,}setpts=PTS/$sp,fps=$fps,scale=$w:-2:flags=lanczos,format=yuv420p"
  if stale "$src" "$mp4"; then
    ffmpeg -v error -y -ss "$ss" -t "$t" -i "$src" -an -vf "$vf" -c:v libx264 -preset slow -crf "$crf" \
      -profile:v high -movflags +faststart -maxrate 3500k -bufsize 7000k "$mp4"
  fi
  if stale "$src" "$webm"; then
    ffmpeg -v error -y -ss "$ss" -t "$t" -i "$src" -an -vf "$vf" -c:v libvpx-vp9 -crf $((crf + 14)) -b:v 0 \
      -row-mt 1 -deadline good -cpu-used 2 "$webm"
  fi
  if stale "$src" "$poster"; then
    ffmpeg -v error -y -ss "$pt" -i "$mp4" -frames:v 1 -q:v 3 "$poster"
  fi
  note "$mp4"; note "$webm"
  local mb; mb=$(du -m "$mp4" | cut -f1)
  (( mb <= 4 )) || echo "WARN $mp4 is ${mb} MB (> 4 MB budget)" | tee -a "$LOG"
}

# ---------------------------------------------------------------- 1 NomadZ kicking
S=nomadz-kicking; K="$R/kicking_t1/offline/goal_v2_report/media"
GR="$R/kicking_t1/reports/goal_2026-11-13/media"
# hero: first ~7 shots of the best model's 100-shot wide-view sequence (MuJoCo validation renders)
vid "$K/gv2mh_best_wide1080p_seq.mp4"            $S best-wide 0 30 1280 1 25 25 1.2
# training film: drone flight over 100 Isaac envs, iteration 0 → 5998 (learning to kick, then goal training)
vid "$GR/film_a1.mp4"                            $S film-a1 0 63 960 1 30 31 52
# the full 100-shot reel, on demand only (controls, preload none)
FULL="$VID/$S/best-wide-full.mp4"
if stale "$K/gv2mh_best_wide1080p_seq.mp4" "$FULL"; then
  ffmpeg -v error -y -i "$K/gv2mh_best_wide1080p_seq.mp4" -an -vf "fps=25,scale=1280:-2,format=yuv420p" -c:v libx264 \
    -preset slow -crf 31 -movflags +faststart "$FULL"
fi
note "$FULL"
# same shot, four learning approaches (MuJoCo): A1 goal-trained | A6 diffusion  /  A7b residual | A3 pure PPO
ARMS="$VID/$S/arms-2x2.mp4"
if stale "$GR/mj_goal_a1c.mp4" "$ARMS"; then
  ffmpeg -v error -y -i "$GR/mj_goal_a1c.mp4" -i "$GR/mj_goal_a6.mp4" -i "$GR/mj_goal_a7b.mp4" -i "$GR/mj_goal_a3.mp4" -an \
    -filter_complex "[0:v]trim=0:4.4,setpts=PTS-STARTPTS,scale=640:-2[a];[1:v]trim=0:4.4,setpts=PTS-STARTPTS,scale=640:-2[b];[2:v]trim=0:4.4,setpts=PTS-STARTPTS,scale=640:-2[c];[3:v]trim=0:0.96,setpts=PTS-STARTPTS,scale=640:-2,tpad=stop_mode=clone:stop_duration=4[d];[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0,trim=0:4.4,format=yuv420p[v]" \
    -map "[v]" -c:v libx264 -preset slow -crf 27 -movflags +faststart "$ARMS"
  ffmpeg -v error -y -i "$ARMS" -c:v libvpx-vp9 -crf 40 -b:v 0 -row-mt 1 "${ARMS%.mp4}.webm"
  ffmpeg -v error -y -ss 2.4 -i "$ARMS" -frames:v 1 -q:v 3 "$IMG/$S/arms-2x2-poster.jpg"
fi
note "$ARMS"
vid "$R/portfolio/Pic/Nomadz/Nomadz_first_demo.mp4" $S k1-lab 0 12 540 1 30 28 2
vid "$K/gv2mh_best_grid.mp4"                     $S kick-grid 0 6.6 1280 1 25 26 6.2

# ---------------------------------------------------------------- 2 Header Net
S=header-net; H="$R/portfolio/resources/header_net"
img "$H/visualizations/output/gradcam_correct_0.png" $S gradcam.png 1800
img "$H/visualizations/output/correct_gallery.png"   $S correct-gallery.jpg 1800
img "$H/report/new_figure/focal_loss_curve.png"       $S focal-loss.png 1400

# ---------------------------------------------------------------- 3 Drone Car
S=drone-car; P="$R/portfolio/Pic"; DR="$P/mech_421/Final_project/report/images"
vid "$P/Transforming.mp4"      $S transform 18 14 960 1.4 30 29 7.5
vid "$P/showcase_all_mode.mp4" $S showcase 8 10 960 1 30 29
vid "$P/IMU_demo.mp4"          $S imu 40 12 960 1 30 29
img "$P/transformer_car_mode.jpg"    $S car-mode.jpg 1800
img "$P/transformer_drone_mode.png"  $S drone-mode.jpg 1800
img "$P/CAD_blowout_transformer.jpg" $S cad-exploded.jpg 1600
img "$DR/flow_chart.png"             $S subsystems.png 1600

# ---------------------------------------------------------------- 4 Subbots
S=subbots; SB="$R/portfolio/Pic/Subbots"; SA="$R/portfolio/steelhead/assets"
img "$SB/Subbots_main.png"          $S steelhead-cad.png 1800
img "$SB/torpedo_CFD.png"           $S torpedo-cfd.png 1600
img "$SB/torpedo_cad.png"           $S torpedo-cad.png 1400
img "$SB/Yolo1.png"                 $S yolo.jpg 1400
img "$SB/Newest_claw+dropper.png"   $S claw-dropper.png 1400
img "$SA/system_architecture_draw_io.drawio.png" $S system-architecture.png 1800

# ---------------------------------------------------------------- 5 Scene-graph localization
S=scene-graph-localization; V="$R/vision_project/docs"
vid "$V/slides/videos/localizer_demo.mp4" $S localizer 0 31 1280 1 10 26 29
vid "$V/slides/videos/hydra_demo.mp4"     $S hydra 0 40 1280 1 10 26 36
img "$V/figures/failures/3rv_04_bf9a3dd7_q1_compact_seg_G4_r4.png" $S failure-3rv04.png 1800
img "$V/figures/failures/3rv_12_0f2f271b_q2_compact_seg_G4_r4.png" $S confirm-3rv12.png 1800

# ---------------------------------------------------------------- 6 PDM4AR
S=pdm4ar; E="$R/ex13_portfolio"
vid "$E/docking_disturbance.mp4" $S docking 0 14.8 720 1 25 27 9
img "$E/trajectories_public.png" $S trajectories.png 1800
img "$E/scvx_convergence.png"    $S scvx-convergence.png 1600
img "$E/scores_vs_ta.png"        $S scores-vs-ta.png 1600
img "$E/penalty_breakdown.png"   $S penalty-breakdown.png 1600

# ---------------------------------------------------------------- 7 CVAIAC dense prediction
S=cvaiac-dense-prediction; C="$R/cvaiac26_team_13"; HA="$R/handout_answer_assets"
img "$C/doc/teaser.png"                          $S teaser.jpg 1800
img "$HA/segmentation_comparison.png"            $S segmentation.jpg 1800
img "$HA/depth_comparison.png"                   $S depth.jpg 1800
img "$C/report/Graphs/optuna_history_pruning.png" $S optuna-history.png 1600
img "$C/report/Graphs/p5_architecture.png"       $S architecture.png 1800

# ---------------------------------------------------------------- 8 CVAIAC LiDAR detection
S=cvaiac-lidar-detection; L="$R/cvaiac26_team_13_project_2/artifacts"
vid "$L/video/detector_demo_canonical.mp4" $S detector 0 24 1280 1 12 27 3
vid "$L/video/drive_through_canonical.mp4" $S drive 0 16 960 1 30 29 8
img "$L/report_figures/ap_curves_all.png"      $S ap-curves.png 1600
img "$L/report_figures/distance_breakdown.png" $S distance-breakdown.png 1600
img "$L/report_figures/evolution_scene0.png"   $S evolution.png 1800

# ---------------------------------------------------------------- 9/10 generated chart data (stethoscope, Stoeber)
python3 -I "$SITE/scripts/make_chart_data.py" "$R" "$SITE/src/data/charts" | tee -a "$LOG"
python3 -I "$SITE/scripts/make_covers.py" "$SITE" | tee -a "$LOG"
S=stoeber-porous-valve; O="$R/portfolio/porous_material/oct/output"
img "$O/sample_01_5micron-xy_3.49micron-z_block_size_effect_cdf.svg" $S pore-cdf.png 1600

# ---- profile photo: kept OUT of src/ so it never ships. To publish: cp private/profile.jpg src/assets/profile/ and set site.photo.show
mkdir -p "$SITE/private"; stale "$R/portfolio/Pic/Profile_pic.jpg" "$SITE/private/profile.jpg" && magick "$R/portfolio/Pic/Profile_pic.jpg" -auto-orient -resize "1000x1000>" -strip -quality 86 "$SITE/private/profile.jpg"; note "$SITE/private/profile.jpg"

echo "---- totals"; du -sh "$IMG" "$VID" | tee -a "$LOG"

# ---- derived: Header Net card cover = the six Grad-CAM frames as a 3×2 grid on the site's dark surface
HN="$IMG/header-net"
if stale "$HN/gradcam.png" "$HN/cover.png"; then
  magick "$HN/gradcam.png" -crop 6x1@ +repage -gravity south -crop 280x262+0+6 +repage miff:- \
    | magick montage - -tile 3x2 -geometry +10+10 -background '#0a0c0f' "$HN/cover.png"
fi
note "$HN/cover.png"

# ---- CVAIAC project 1: course Codabench leaderboard screenshot (team 13 = 1st)
img "$R/cvaiac26_team_13/leaderboard_result.png" cvaiac-dense-prediction leaderboard.png 1800

# ---- PDM4AR ex14 (multi-agent goal collection). Renders come from the official simulator run on the final code:
#   1) docker run … idscfrazz/pdm4ar2026 … python scripts/pdm4ar_ex14/extract.py config_{1,2,3}.yaml  → .cache/pdm4ar-ex14/*.json
#   2) python3 scripts/pdm4ar_ex14/render.py .cache/pdm4ar-ex14 .cache/pdm4ar-ex14/render
S=pdm4ar-warehouse; W="$SITE/.cache/pdm4ar-ex14/render"
vid "$W/config_3.mp4" $S config-3 0 30 1080 1 25 25 9
vid "$W/config_2.mp4" $S config-2 0 20 1080 1 25 25 8
vid "$W/config_1.mp4" $S config-1 0 40 1080 1 25 25 12
img "$W/config_3_routes.png" $S routes-3.png 1400
img "$W/config_2_routes.png" $S routes-2.png 1400
img "$W/timeline.png"        $S timeline.png 1600
img "$R/pdm4ar_final_project/cp_congestion_example.png" $S congestion-early.png 1400
