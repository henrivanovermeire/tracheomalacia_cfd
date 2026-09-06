set terminal cairolatex pdf color size 16cm,13cm font ",9"
set output "figures/assignment5_mesh_metrics.tex"
set datafile separator comma
set multiplot layout 2,2 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set xlabel "Number of volume cells"
set format x "%.1t$\\times10^{%T}$"
set ylabel "Resistance (Pa/(L/min))"
set title "Resistance (Pa/(L/min))"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:13 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Right-lung flow fraction (\\%)"
set title "Right-lung flow fraction (\\%)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:16 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Right-superior share of right flow (\\%)"
set title "Right-superior share of right flow (\\%)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:18 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Matched-section peak velocity (m/s)"
set title "Matched-section peak velocity (m/s)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:15 every ::1 with linespoints lw 2 pt 7 notitle
unset multiplot
unset output
