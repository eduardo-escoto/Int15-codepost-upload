input_dir=$1;
output_dir=$2;
assignment_name=$3;

python preprocess-add-grade.py $input_dir $output_dir $assignment_name;

for notebook in output_dir/*.ipynb;
do
    echo "Now executing:" $notebook "🤔";
    jupyter nbconvert --to notebook --execute $notebook;
    echo "Notebook:" $notebook "executed 🎉🎊";
done

echo "All notebooks autograded and executed 🎉🎊"