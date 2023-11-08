from ryven import node


class ImageNode(node.Node):
    def __init__(self):
        super().__init__()

        self.add_output('image', '')
        self.add_output('width', 0)
        self.add_output('height', 0)

    def compute(self):
        # Load image and get its dimensions
        image_path = 'path/to/image.jpg'
        #image = Image.open(image_path)
        width, height = (1024,1024) #image.size

        # Output image and dimensions
        self.set_output_val('image', 'foo')
        self.set_output_val('width', width)
        self.set_output_val('height', height)
