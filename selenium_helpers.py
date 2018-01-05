class element_does_not_have_text(object):
  def __init__(self, container, text):
    self.container = container
    self.text = text

  def __call__(self, driver):
    if self.text not in self.container.text:
      return self.container
    else:
      return False