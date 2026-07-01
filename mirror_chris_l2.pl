# Source for L2 files
$srcdir = "/fs/scratch/PCON0003/cond0007/Jun26/H1/sim/L2";
# where to put the symbolic links
$targetdir = "/fs/ess/PCON0003/nddalal/impreprocess_e2e/outputs/L2";

# Run over files in the source directory
for $f (split ' ', `ls -1 $srcdir/`) {
    # filter on extensions
    if ($f =~ m/\.(asdf|fits)$/) {
        print("Linking $f ...\n");
        $command = "ln -s $srcdir/$f $targetdir/$f";
        system $command;
    }
}