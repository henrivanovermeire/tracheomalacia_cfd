set terminal cairolatex pdf color size 16cm,13cm font ",9"
set output "figures/assignment5_mesh_differences.tex"
set datafile separator comma
set multiplot layout 2,2 rowsfirst
set grid xtics ytics back lc rgb "#d0d0d0"
set xlabel "Number of volume cells"
set format x "%.1t$\\times10^{%T}$"
set ylabel "Difference from finest mesh (\\%)"
set title "Resistance (Pa/(L/min))"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:20 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Difference from finest mesh (\\%)"
set title "Right-lung flow fraction (\\%)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:21 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Difference from finest mesh (\\%)"
set title "Right-superior share of right flow (\\%)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:22 every ::1 with linespoints lw 2 pt 7 notitle
set ylabel "Difference from finest mesh (\\%)"
set title "Matched-section peak velocity (m/s)"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/mesh_sensitivity.csv" using 3:23 every ::1 with linespoints lw 2 pt 7 notitle
unset multiplot
unset output
