set terminal cairolatex pdf color size 15cm,8cm font ",10"
set output "figures/assignment6_breathing_waveform.tex"
set datafile separator comma
set grid xtics ytics back lc rgb "#d0d0d0"
set key off
set xlabel "Time (s)"
set ylabel "Inlet flow rate (L/min)"
set title "Sinusoidal breathing waveform"
set xzeroaxis lw 1 lc rgb "black"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/breathing_waveform.csv" using 1:3 every ::1 with lines lw 2.2 lc rgb "#2166ac"
unset output
