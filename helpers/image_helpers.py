# function to handle image upload
def upload_image_to(instance, filename):
    return 'crops/uploaded/{filename}'.format(filename=filename)