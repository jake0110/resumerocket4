{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.python-docx
    pkgs.python311Packages.anthropic
  ];
}