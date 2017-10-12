# Indus Script OCR

To automatically locate text patches/regions, segment individual symbols/characters from those regions and also identify each symbol/character belonging to the Indus Script, given images of Indus seals from archaeological sites, using image processing and deep learning techniques.

View our research article titled "__Deep Learning the Indus Script__" arXived at: [arXiv:1702.00523v1](https://arxiv.org/abs/1702.00523v1)


## Press Coverage:

- [The Verge](http://www.theverge.com/2017/1/25/14371450/indus-valley-civilization-ancient-seals-symbols-language-algorithms-ai#EQQA6r)
- [The Hindu](http://www.thehindu.com/sci-tech/science/chennai-team-taps-ai-to-read-indus-script/article17448690.ece)
- [Times of India](http://timesofindia.indiatimes.com/city/chennai/app-may-help-decipher-indus-valley-symbols/articleshow/57281369.cms)
- [SBS Radio, Australia](http://www.sbs.com.au/yourlanguage/tamil/en/content/app-decipher-ancient-symbols?language=en)


## Deploying the app

- Setup the GPU machine to run the service,
  - Install latest nvidia drivers, from `http://www.geforce.com/drivers`
  - Install the nvidia-docker plug-in over docker, from `https://github.com/NVIDIA/nvidia-docker/releases`
  - Make sure you have `git-lfs` installed (https://git-lfs.github.com/)

- Launch the service,
  - Build the docker image: `nvidia-docker build --no-cache=true -t indus-script-ocr:latest .`
  - To launch a docker container: `nvidia-docker run -it -v "$PWD":/root/workspace --rm --env-file app.env --name indus-script-ocr-service indus-script-ocr:latest`

## Talks

- **Indian Deep Learning Initiative (IDLI):** [slide deck](https://github.com/tpsatish95/talks/blob/master/Deep\%20learning\%20based\%20OCR\%20engine\%20for\%20the\%20Indus\%20script\%20-\%20IDLI\%20Talk.pdf), [video](https://www.youtube.com/watch?v=qPF1oR9yMNY}), [link](https://www.facebook.com/groups/idliai/) 
- **ThoughtWorks Geek Night:** [slide deck](https://github.com/tpsatish95/talks/blob/master/Deep\%20learning\%20based\%20OCR\%20engine\%20for\%20the\%20Indus\%20script\%20-\%20TW\%20Geek\%20Night.pdf), [video](https://www.youtube.com/watch?v=g7v4QaCD-UQ), [link](https://twchennai.github.io/geeknight/edition-43.html) 
- **ChennaiPy:** [link](http://chennaipy.org/may-2017-meet-minutes.html) 
- **Anthill Inside 2017:** [proposal](https://anthillinside.talkfunnel.com/2017/15-deep-learning-based-ocr-engine-for-the-indus-scrip)

## Citation

Please cite `indus-script-ocr` in your publications if it helps your research:

    @article{palaniappan2017deep,
    title={Deep Learning the Indus Script},
    author={Palaniappan, Satish and Adhikari, Ronojoy},
    journal={arXiv preprint arXiv:1702.00523},
    year={2017}
    }
