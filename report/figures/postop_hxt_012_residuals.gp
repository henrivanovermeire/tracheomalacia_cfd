set terminal cairolatex pdf color size 15cm,9cm font ",10"
set output "figures/postop_hxt_012_residuals.tex"
set datafile separator comma
set key outside top center horizontal maxrows 2
set grid xtics ytics mxtics mytics back lc rgb "#d0d0d0"
set logscale y
set format y "$10^{%T}$"
set xlabel "SIMPLE iteration"
set ylabel "Initial residual"
set xrange [1:*]
set yrange [1e-7:1]
set title "Postoperative steady-solver convergence"
plot "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_hxt_012_residuals.csv" using 1:2 every ::1 with lines lw 1.5 title "$U_x$", \
     "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_hxt_012_residuals.csv" using 1:3 every ::1 with lines lw 1.5 title "$U_y$", \
     "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_hxt_012_residuals.csv" using 1:4 every ::1 with lines lw 1.5 title "$U_z$", \
     "/home/hvoverme/tracheomalacia_cfd/assignment/data/postop_hxt_012_residuals.csv" using 1:5 every ::1 with lines lw 1.5 title "$p$", \
     1e-6 with lines dt 2 lw 1.2 lc rgb "black" title "$U$ criterion", \
     1e-5 with lines dt 3 lw 1.2 lc rgb "#666666" title "$p$ criterion"
unset output
