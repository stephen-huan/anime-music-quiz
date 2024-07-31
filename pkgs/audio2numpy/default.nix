{ lib
, fetchFromGitHub
, buildPythonPackage
, setuptools
, numpy
, ffmpeg
, pytestCheckHook
}:

buildPythonPackage {
  pname = "audio2numpy";
  version = "0.1.3-unstable-2021-09-09";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "wiccy46";
    repo = "audio2numpy";
    rev = "c1759798b084f75d4e03739cf4e05d84861c4003";
    sha256 = "sha256-XTkeBiKYBtHrY+knmhajDnMW4JB9HMlOiFyEHKojmXM=";
  };

  build-system = [
    setuptools
  ];

  buildInputs = [
    ffmpeg
  ];

  dependencies = [
    numpy
  ];

  nativeCheckInputs = [
    pytestCheckHook
    ffmpeg
  ];

  pythonImportsCheck = [
    "audio2numpy"
  ];

  meta = with lib; {
    description = "load audio files into numpy array";
    homepage = "https://github.com/wiccy46/audio2numpy";
    license = licenses.mit;
    maintainers = with maintainers; [ stephen-huan ];
  };
}
