set terminal cairolatex pdf color size 15cm,11cm font ",9"
set output "assignment6_cycle_response.tex"
set datafile separator comma
set datafile missing ""
set multiplot layout 2,2 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set xrange [0:2]
set key top right
set ylabel "Flow rate (L/min)"
set title "Postoperative breathing-cycle response"
set xzeroaxis lw 1 lc rgb "black"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_metrics.csv" using 1:($12*60000) every ::1 with lines lw 2 lc rgb "#2166ac" title "Section flow"
set ylabel "$\Delta P$ (Pa)"
unset key
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_metrics.csv" using 1:11 every ::1 with lines lw 2 lc rgb "#b2182b"
set xlabel "Time (s)"
set ylabel "$R$ (Pa/(L/min))"
set yrange [0:30]
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_metrics.csv" using 1:14 every ::1 with lines lw 2 lc rgb "#4d9221" title "Transient CFD", \
     15.359 with lines dt 2 lw 1.5 lc rgb "#444444" title "Steady coarse-mesh value"
set xlabel "Time (s)"
set ylabel "Qualitative resistance (a.u.)"
set yrange [0:3.5]
set title "Conceptual anatomical comparison (not CFD)"
plot 1.0+0.15*abs(sin(pi*x)) with lines lw 2 lc rgb "#2166ac" title "Postoperative", \
     2.5+0.45*abs(sin(pi*x)) with lines dt 2 lw 2 lc rgb "#b2182b" title "Preoperative expectation"
unset multiplot
unset output
