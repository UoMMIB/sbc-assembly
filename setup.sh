# Set environment variables:
BASEDIR=$(pwd)
VIENNA_VERSION="ViennaRNA-2.4.13"

echo $BASEDIR

# Install Homebrew (https://brew.sh/):
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install brew dependencies:
brew install gawk


# Install ViennaRNA (https://www.tbi.univie.ac.at/RNA/):
curl -fsSL https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_4_x/$VIENNA_VERSION.tar.gz -o $TMPDIR/$VIENNA_VERSION.tar.gz
tar zxvf $TMPDIR/$VIENNA_VERSION.tar.gz -C $TMPDIR/
cd $TMPDIR/$VIENNA_VERSION
./configure \
	CC="gcc -arch x86_64" \
	CXX="g++ -arch x86_64" \
	CPP="gcc -E" CXXCPP="g++ -E" \
	--disable-openmp --without-kinfold --without-forester --without-rnalocmin
make
make install

# Install Python packages with pip:
cd $BASEDIR
pip install --upgrade pip
pip install -r requirements.txt --upgrade