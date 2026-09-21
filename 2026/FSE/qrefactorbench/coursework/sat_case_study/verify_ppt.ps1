param([string]$PresentationPath, [string]$PdfPath, [string]$RenderDirectory)
$ErrorActionPreference = "Stop"
$alreadyRunning = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $deck = $app.Presentations.Open($PresentationPath, $true, $false, $false)
    if ($deck.Slides.Count -ne 8) { throw "Expected exactly 8 slides" }
    $deck.SaveAs($PdfPath, 32)
    $deck.Export($RenderDirectory, "PNG", 1600, 900)
    Write-Output "PowerPoint opened all 8 slides; PDF and PNG export succeeded."
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if (($null -ne $app) -and (-not $alreadyRunning)) { $app.Quit() }
}
