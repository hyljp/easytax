import os
import shutil
from PIL import Image, ImageTk


class ImageNavigator:
    SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

    def __init__(self):
        self.image_files = []
        self.current_index = -1
        self.current_image_path = None
        self._photo = None  # prevent GC of PhotoImage

    def set_folder(self, folder_path):
        self.image_files = []
        for root, _, files in os.walk(folder_path):
            for fname in files:
                if fname.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    self.image_files.append(os.path.join(root, fname))
        self.image_files.sort()
        self.current_index = -1
        self.current_image_path = None

    @property
    def has_images(self):
        return len(self.image_files) > 0

    @property
    def count(self):
        return len(self.image_files)

    @property
    def current_position(self):
        if self.current_index < 0:
            return 0
        return self.current_index + 1

    def next_image(self):
        if not self.image_files:
            return None
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.current_image_path = self.image_files[self.current_index]
        return self.current_image_path

    def previous_image(self):
        if not self.image_files:
            return None
        self.current_index = (self.current_index - 1) % len(self.image_files)
        self.current_image_path = self.image_files[self.current_index]
        return self.current_image_path

    def remove_current(self):
        if self.current_image_path and self.current_image_path in self.image_files:
            self.image_files.remove(self.current_image_path)
            if self.image_files:
                # Step back so the next call to current() or next_image()
                # lands on the item that shifted into this position.
                self.current_index = (self.current_index - 1) % len(self.image_files)
            else:
                self.current_index = -1
            self.current_image_path = None

    def current(self):
        """Return the image at current_index + 1 (the next unprocessed image) without skipping."""
        if not self.image_files:
            return None
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.current_image_path = self.image_files[self.current_index]
        return self.current_image_path

    def draw_on_canvas(self, canvas, image=None, image_path=None, zoom=1.0):
        if image is None and image_path is None:
            image_path = self.current_image_path
        if image is None and image_path:
            image = Image.open(image_path)

        if image is None:
            return

        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        img_w, img_h = image.size
        fit_scale = min(canvas_w / img_w, canvas_h / img_h)
        scale = fit_scale * zoom
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized = image.resize((new_w, new_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(resized)

        canvas.delete("all")
        x_offset = (canvas_w - new_w) // 2
        y_offset = (canvas_h - new_h) // 2
        canvas.create_image(x_offset, y_offset, anchor="nw", image=self._photo)


def move_file(src, dest_dir, date, comment, price):
    os.makedirs(dest_dir, exist_ok=True)
    _, ext = os.path.splitext(src)
    base = f"{date}_{price}_{comment}"
    new_name = f"{base}{ext}"
    dest = os.path.join(dest_dir, new_name)

    counter = 1
    while os.path.exists(dest):
        new_name = f"{base}_{counter}{ext}"
        dest = os.path.join(dest_dir, new_name)
        counter += 1

    shutil.move(src, dest)
