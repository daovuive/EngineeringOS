$root = "D:\projects\EngineeringOS\"
$folders = @(
    "docs","knowledge","agents","prompts","tools",
    "scripts","configs","memory","logs","experiments","tests"
)
foreach ($f in $folders) {
    $file = "$root\$f\README.md"
    if (-not (Test-Path $file)) {
        "# $f folder" | Out-File -FilePath $file -Encoding UTF8
    }
}
