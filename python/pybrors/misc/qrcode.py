# File: misc/qrcode.py

# Import packages and submodules
import qrcode
import qrcode.image.svg

# Import classes and methods
from PIL import Image

class QRcode:
    """
    A class for generating QR codes.

    This class provides methods to generate a QR code with contact
    vCard information and add a logo. It can also save the generated QR
    code as a PNG image.
    """

    def __init__(self) -> None:
        """
        Initialize the object.

        This function is the constructor of the class. It initializes
        the object and sets up the QRCode generator with the specified
        parameters.
        """
        self.qrcode = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        self.logo = None

    def add_contact_vcard(self) -> None:
        """
        Add contact vcard in the QR code.

        This function fills the vcard with the contact information,
        including the person's name, organization, title, email, and
        telephone number.
        """
        # Fill vcard
        self.qrcode.add_data("BEGIN:VCARD\r\nVERSION:3.0\r\n")
        self.qrcode.add_data("N:Robert;Benjamin\r\n")
        self.qrcode.add_data("ORG:United Imaging Healthcare;\r\n")
        self.qrcode.add_data("TITLE:Lead MRI Research Collaboration Scientist\r\n")
        self.qrcode.add_data("EMAIL:benjamin.robert@united-imaging.com\r\n")
        self.qrcode.add_data("TEL:+33 6 51 06 75 27\r\n")
        self.qrcode.add_data("END:VCARD\r\n")

    def add_logo(self, file_path: str = None) -> None:
        """
        Adds a logo to the QRcode.

        Parameters
        ----------
        file_path : str
            The path to the logo file. Defaults to None.
        """
        # Check if logo should be selected of if it is provided
        if file_path is None:
            return None

        self.logo = file_path

    def save_png(self, file_path: str = None, color: str = "#000000") -> None:
        """
        Save a PNG image of the generated QR code.

        Parameters
        ----------
        file_path : str
            The file path to save the PNG image. If not provided, the
            image will not be saved. Defaults to None.
        color : str
            The color of the QR code. Defaults to "#000000".
        """
        # Generate qrcode
        self.qrcode.make(fit=True)
        img = self.qrcode.make_image(fill_color=color, back_color="white")

        # Add logo to qrcode
        logo      = Image.open(self.logo)
        basewidth = 250
        wpercent  = basewidth / float(logo.size[0])
        hsize     = int((float(logo.size[1]) * float(wpercent)))
        logo      = logo.resize((basewidth, hsize), Image.LANCZOS)
        pos       = ((img.size[0] - logo.size[0])//2, (img.size[1] - logo.size[1])//2)
        img.paste(logo, pos)

        # Save qrcode
        img.save(file_path)
