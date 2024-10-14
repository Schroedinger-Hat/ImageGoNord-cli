# ImageGoNord client 

ImageGoNord is a tool that can convert your rgb images to nordtheme palette.

You can find more information here: [ImageGoNord](https://github.com/Schrodinger-Hat/ImageGoNord)

This repository is a client, written in python, that can convert any sort of image into a nordtheme palette image.

## Getting Started
Include any essential instructions for:

- Getting it:
  ```
  git clone https://github.com/Schrodinger-Hat/ImageGoNord-cli
  ```

- Install dependencies
  ```shell
  pip install -r requirements.txt
  ```
- Running it
  ```shell
  export PYTHONPATH=$PYTHONPATH:$PWD/src:$PWD/tests
  python src/image_go_nord_client --img='<path_to_your_image>' 
  ```
  Or if you prefer
  ```shell
  export PYTHONPATH=$PYTHONPATH:$PWD/src:$PWD/tests
  cd src
  python image_go_nord_client --img='<path_to_your_image>' 
  ```

The algorithm can take some time (we are working on improving it), you can find the result with the name *nord.png*.

You can define some more configuration and use different palettes, find more using:

```shell
python src/image_go_nord_client --img='<path_to_your_image>' 
```

### Contributing
- Follow the contributor guidelines
- Follow the code style / requirements
- Format for commit messages


# Authors
[TheJoin95](https://github.com/TheJoin95) & [Wabri](https://github.com/Wabri)

**NOTE**: we are not (yet) affiliated with the Nordtheme or [Arcticicestudio](https://github.com/arcticicestudio).

# Credits

[Nordtheme](https://www.nordtheme.com/)
