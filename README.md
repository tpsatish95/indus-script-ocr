# Indus Script OCR

To automatically locate text patches/regions, segment individual symbols/characters from those regions and also identify each symbol/character belonging to the Indus Script, given images of Indus seals from archaeological sites, using image processing and deep learning techniques.

View our research article titled "__Deep Learning the Indus Script__" arXived at: [arXiv:1702.00523v1](https://arxiv.org/abs/1702.00523v1)


## Press Coverage:

- [The Verge](http://www.theverge.com/2017/1/25/14371450/indus-valley-civilization-ancient-seals-symbols-language-algorithms-ai#EQQA6r)
- [The Hindu](http://www.thehindu.com/sci-tech/science/chennai-team-taps-ai-to-read-indus-script/article17448690.ece)
- [Times of India](http://timesofindia.indiatimes.com/city/chennai/app-may-help-decipher-indus-valley-symbols/articleshow/57281369.cms)
- [SBS Radio, Australia](http://www.sbs.com.au/yourlanguage/tamil/en/content/app-decipher-ancient-symbols?language=en)


# Deploying the app

- Setup the GPU machine to run the service,
  - Install latest nvidia drivers, from `http://www.geforce.com/drivers`
  - Install the nvidia-docker plug-in over docker, from `https://github.com/NVIDIA/nvidia-docker/releases`
  - Make sure you have `git-lfs` installed (https://git-lfs.github.com/)

- Launch the service,
  - Build the docker image: `nvidia-docker build --no-cache=true -t indus-script-ocr:latest .`
  - To launch a docker container: `nvidia-docker run -it -v "$PWD":/root/workspace --rm --env-file app.env --name indus-script-ocr-service indus-script-ocr:latest`


## Citation

Please cite `indus-script-ocr` in your publications if it helps your research:

    @article{palaniappan2017deep,
    title={Deep Learning the Indus Script},
    author={Palaniappan, Satish and Adhikari, Ronojoy},
    journal={arXiv preprint arXiv:1702.00523},
    year={2017}
    }
