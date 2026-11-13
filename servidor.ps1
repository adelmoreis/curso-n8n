$port = 8080
$root = $PSScriptRoot
$types = @{ '.html'='text/html; charset=utf-8'; '.js'='text/javascript'; '.css'='text/css'; '.png'='image/png'; '.jpg'='image/jpeg'; '.svg'='image/svg+xml'; '.json'='application/json'; '.ico'='image/x-icon' }
$l = New-Object System.Net.HttpListener
try { $l.Prefixes.Add("http://+:$port/"); $l.Start(); Write-Host "Rede liberada." }
catch { $l = New-Object System.Net.HttpListener; $l.Prefixes.Add("http://localhost:$port/"); $l.Start(); Write-Host "Somente neste PC (para abrir em outros aparelhos, instale o Python ou execute como administrador)." }
while ($l.IsListening) {
  $c = $l.GetContext()
  $p = $c.Request.Url.LocalPath.TrimStart('/'); if ($p -eq '') { $p = 'index.html' }
  $f = Join-Path $root $p
  if ((Test-Path $f -PathType Leaf) -and ($f.StartsWith($root))) {
    $b = [System.IO.File]::ReadAllBytes($f); $e = [System.IO.Path]::GetExtension($f).ToLower()
    $c.Response.ContentType = if ($types.ContainsKey($e)) { $types[$e] } else { 'application/octet-stream' }
    $c.Response.OutputStream.Write($b, 0, $b.Length)
  } else { $c.Response.StatusCode = 404 }
  $c.Response.Close()
}
