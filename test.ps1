param (
    [Parameter(Position = 0)]
    [string]$gitName,

    [Parameter(Position = 1)]
    [string]$dirname
)
echo $dirname

cd $dirname
echo "# AUTO CHECKIN --" >> README.md
git init
git add README.md

git add . ':!.env'

git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/MaheshUmale/my-article-writer.git
git push -u origin main
cd D:\py_code_workspace


