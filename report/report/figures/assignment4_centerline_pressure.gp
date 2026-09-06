set terminal cairolatex pdf color size 15cm,8.5cm font ",10"
set output "figures/assignment4_centerline_pressure.tex"
set datafile separator comma
set key off
set grid xtics ytics back lc rgb "#d0d0d0"
set xlabel "Centerline distance from mapped superior limit (mm)"
set ylabel "Area-interpolated centerline pressure (Pa)"
set title "Postoperative pressure through the anatomically matched region"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_assignment4_centerline_pressure.csv" using 1:3 every ::1 with lines lw 2.2 lc rgb "#2166ac"
unset output
