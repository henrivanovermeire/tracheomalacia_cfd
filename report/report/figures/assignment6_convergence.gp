set terminal cairolatex pdf color size 15cm,10cm font ",9"
set output "assignment6_convergence.tex"
set datafile separator comma
set multiplot layout 2,1 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set key top right
set xrange [0:2]
set ylabel "Courant number"
set title "Adaptive timestep control"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_convergence.csv" using 1:2 every ::1 with lines lw 1.5 lc rgb "#4d9221" title "Mean Co", \
     "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_convergence.csv" using 1:3 every ::1 with lines lw 1.2 lc rgb "#c51b7d" title "Maximum Co", \
     "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_convergence.csv" using 1:(strcol(5) eq "False" ? $3 : 1/0) every ::1 with points pt 7 ps 0.35 lc rgb "#d73027" title "Outer criterion not met"
set xlabel "Time (s)"
set ylabel "Time step (s)"
set format y "%.1t$\times10^{%T}$"
set title "Physical timestep"
unset key
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_transient_coarse_poc_convergence.csv" using 1:4 every ::1 with lines lw 1.5 lc rgb "#2166ac"
unset multiplot
unset output
