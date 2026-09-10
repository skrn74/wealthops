Remove-Item Env:AWS_ACCESS_KEY_ID -ErrorAction SilentlyContinue
Remove-Item Env:AWS_SECRET_ACCESS_KEY -ErrorAction SilentlyContinue
Remove-Item Env:AWS_SESSION_TOKEN -ErrorAction SilentlyContinue

$role = aws sts assume-role `
  --role-arn arn:aws:iam::076194732097:role/WealthOpsEKSProvisioner `
  --role-session-name WealthOpsEKSSetup | ConvertFrom-Json

$env:AWS_ACCESS_KEY_ID = $role.Credentials.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $role.Credentials.SecretAccessKey
$env:AWS_SESSION_TOKEN = $role.Credentials.SessionToken