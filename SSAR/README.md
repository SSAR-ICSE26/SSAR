# SSAR

## 1. Introduction

This is an architecture recovery tool that supports the following features:

1. Input the project directory, provide the dependencies .csv file and the ground_truth .json file, and the files listed in ground_truth will be analyzed.
   - If the ground_truth file is not provided, all code files in the main language of the project will be analyzed.
2. The user can specify the resolution (default 1.05) of community detection to control the number of clusters generated.


## 2. Installation

### 2.1 Git Clone

Clone the project from git. And `cd` to the project root:

```
git clone https://github.com/SSAR-ICSE26/SSAR.git
cd SSAR
```

### 2.2 Install requirements

Enter the SSAR directory, and install the requirements:

```
cd SSAR
pip install -r requirements.txt
```

## 3. Dependency Extraction

Dependencies can be extracted using analysis tools such as *Understand*.

The input format for dependency files in our tool is:

```
From File,To File
relative/path/to/fileA,relative/path/to/fileB
relative/path/to/fileA,relative/path/to/fileC
relative/path/to/fileB,relative/path/to/fileC
...
```

For details, you can check the contents of the HDC/HDC_dep.csv file we provided.

## 3. Usage

```
usage: main.py [-h] [-g] [-r] projectpath dependency

SSAR: A Novel Software Architecture Recovery Approach Enhancing Accuracy and Scalability

positional arguments:
  projectpath         path to the project
  dependency          path to the dependency .csv file

options:
  -h, --help          show this help message and exit
  -g , --gt           path to the ground_truth .json file (if not provided, all code files in the project will be analyzed)
  -r , --resolution   resolution ( > 1 ) for community detection (if not provided, defaults to 1.05)
```

## 4. An Example

We provide the *distributed camera* project, along with dependency and ground_truth file in folder *HDC/*. <br>
So you can just run the following command to test SSAR:
```
python ./main.py ./distributed_camera ./HDC_dep.csv -g ./HDC_gt.json -r 1.05
```

The first run of the program may take some time. After it is finished, a *result* folder will be created in the current directory to hold the architecture recovery results like *result/distributed_camera/distributed_camera.rsf*.

## 5. Optimal Resolution For Project 

| **Project** | **resolution** |
|:-----------:|:--------------:|
| ArchStudio  |      1.2       |
|    Bash     |      1.05      |
|  Chromium   |      1.05      |
|   Hadoop    |      1.1       |
|     HDC     |      1.05      |
|     HDF     |      1.1       |
|     ITK     |      1.05      |
|   Libxml2   |      1.2       |
|    OODT     |      1.2       |

## 6. Dataset link

- ArchStudio4: https://github.com/isr-uci-edu/ArchStudio4 (commit ba6d9ee)
- bash-4.2: https://ftp.gnu.org/gnu/bash/bash-4.2.tar.gz
- chromium: (svn-171054, tag: 23.0.1271.97)
- hadoop-0.19.0: https://github.com/apache/hadoop (commit f9ca84)
- distributed camera: https://gitee.com/openharmony/distributed_camera (commit 46ff87)
- drivers framework: https://gitee.com/openharmony/drivers_framework (commit 0e196f)
- ITK: https://github.com/InsightSoftwareConsortium/ITK (commit 01661cc)
- libxml2: https://github.com/GNOME/libxml2 (commit d5e22ef)
- oodt-0.2: https://github.com/apache/oodt (commit e927bc) 


