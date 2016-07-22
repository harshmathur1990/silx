# coding: utf-8
#/*##########################################################################
# Copyright (C) 2004-2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# #########################################################################*/
"""
This module is a refactored version of
*PyMca5.PyMcaGui.math.fitting.QScriptOption*

It defines a dialog widget with customizable tabs, storing all user input in
an internal dictionary. This is used by FitWidget to set advanced fit
configuration parameters.

Example::

    >>> from silx.gui import qt
    >>> from silx.gui.fit.QScriptOption import QScriptOption
    >>> app = qt.QApplication([])
    >>> sheet1 = {'notetitle': "First Sheet",
    ...           'fields': (["Label", 'Text displayed in the first tab'],
    ...                      ["EntryField", 'entry1', 'Type something here'],
    ...                      ["EntryField", 'entry2', 'Type something here too'],
    ...                      ["CheckField", 'checkbox1', 'Check this box'])}
    >>> sheet2 = {'notetitle': "Second Sheet",
    ...           'fields': (["Label", 'Text displayed in the second tab'],
    ...                      ["EntryField", 'entry3', 'Type something here as well'],
    ...                      ["CheckField", 'checkbox2', 'Check this other box'])}
    >>> qso = QScriptOption(sheets=(sheet1, sheet2))
    >>> qso.show()
    >>> app.exec_()

After interacting with the dialog, you can click the Ok button. Your user
input is available as a dictionary called :attr:`output`::

    >>> print(qso.output)
    {'entry2': '1337', 'checkbox1': 1, 'checkbox2': 0,
    'entry1': 'my user input', 'entry3': 'hello'}

"""
import sys
from collections import OrderedDict
from silx.gui import qt

__authors__ = ["V.A. Sole", "P. Knobel"]
__license__ = "MIT"
__date__ = "08/07/2016"


QTVERSION = qt.qVersion()

_tuple_type = type(())

# def uic_load_pixmap_RadioField(name):
#     pix = qt.QPixmap()
#     m = qt.QMimeSourceFactory.defaultFactory().data(name)
#
#     if m:
#         qt.QImageDrag.decode(m, pix)
#
#     return pix


class TabSheets(qt.QDialog):
    """QDialog widget with a variable number of tabs and
    a few predefined optional buttons (*OK, Cancel, Help, Defaults)* at the
    bottom.

    QPushButton attributes:

        - :attr:`buttonHelp`
        - :attr:`buttonDefaults`
        - :attr:`buttonOk` (connected to :meth:`QDialog.accept`)
        - :attr:`buttonCancel` (connected to :meth:`QDialog.reject`)

    QTabWidget:
        - :attr:`tabWidget`

    """
    def __init__(self, parent=None, modal=False, nohelp=True, nodefaults=True):
        """

        :param parent: parent widget
        :param modal: If ``True``, make dialog modal (block input to other
            visible windows). Default is ``False``.
        :param nohelp: If ``True`` (default), don't add *help* button
        :param nodefaults: If ``True`` (default), don't add *Defaults* button
        """
        qt.QDialog.__init__(self, parent)
        self.setWindowTitle(str("TabSheets"))
        self.setModal(modal)

        tabsheetslayout = qt.QVBoxLayout(self)
        tabsheetslayout.setContentsMargins(11, 11, 11, 11)
        tabsheetslayout.setSpacing(6)

        self.tabWidget = qt.QTabWidget(self)

        self.Widget8 = qt.QWidget(self.tabWidget)
        self.Widget9 = qt.QWidget(self.tabWidget)
        self.tabWidget.addTab(self.Widget8, str("Tab"))
        self.tabWidget.addTab(self.Widget9, str("Tab"))

        tabsheetslayout.addWidget(self.tabWidget)

        layout2 = qt.QHBoxLayout(None)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setSpacing(6)

        if not nohelp:
            self.buttonHelp = qt.QPushButton(self)
            self.buttonHelp.setText(str("Help"))
            layout2.addWidget(self.buttonHelp)

        if not nodefaults:
            self.buttonDefaults = qt.QPushButton(self)
            self.buttonDefaults.setText(str("Defaults"))
            layout2.addWidget(self.buttonDefaults)
        spacer = qt.QSpacerItem(20, 20,
                                qt.QSizePolicy.Expanding,
                                qt.QSizePolicy.Minimum)
        layout2.addItem(spacer)

        self.buttonOk = qt.QPushButton(self)
        self.buttonOk.setText(str("OK"))
        layout2.addWidget(self.buttonOk)

        self.buttonCancel = qt.QPushButton(self)
        self.buttonCancel.setText(str("Cancel"))
        layout2.addWidget(self.buttonCancel)
        tabsheetslayout.addLayout(layout2)

        self.buttonOk.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)


class QScriptOption(TabSheets):
    """
    This is the main widget in the module. It provides a dialog presenting
    multiple tabs to the user. Each tab, or *sheet*, can contain a variable
    number of *fields*, which can be simple text labels or input fields such
    as text entries and check-boxes.

    When the user is done filling all the fields, he clicks the *OK* button
    and the program can resume. The user input data can be accessed in a
    dictionary :attr:`output`.

    It is possible to supply a default dictionary to pre-fill the fields.
    The widget has a defaults button to allow the user to reinitialize all
    fields to the values in the default dict. The keys in this dictionary
    must match the names of the fields (non-matching keys are just ignored).

    Entry fields take strings as values. Checkbox fields take 1 (*checked*)
    or 0 (*un-checked*) as possible values.
    """

    def __init__(self, parent=None, name=None, modal=True,
                 sheets=(), default=None, nohelp=True, nodefaults=True):
        """

        :param parent: Parent widget
        :param name: Window title. If ``None``, use *"TabSheets"*
        :param modal: If ``True``, make dialog modal (block input to other
            visible windows).
        :param sheets: Tuple of dictionaries containing parameters for
            sheets/tabs.
            An example of valid dictionary illustrating the
            format is::

                {'notetitle': "First Sheet",
                 'fields': (["Label", 'Simple Entry'],
                            ["EntryField", 'entry', 'MyLabel'],
                            ["CheckField", 'label', 'Check Label'])}

            The string in the ``notetitle`` item is used as sheet/tab name.
            The ``fields`` item is used as a parameter for :class:`FieldSheet`.

        :param default: Default dictionary
        :param nohelp: If ``True``, don't add *help* button
        :param nodefaults: If ``True``, don't add *Defaults* button
        :param name: Window title. If ``None``, use *"TabSheets"*
        """
        TabSheets.__init__(self, parent, modal,
                           nohelp, nodefaults)
        if default is None or not hasattr(default, "keys"):
            default = {}

        if name is not None:
            self.setWindowTitle(str(name))

        self.sheets = OrderedDict()
        """Ordered dictionary indexed by tab/sheet names , and containing
        :class:`FieldSheet` objects
        """

        self.default = default
        """Default dictionary used to reinitialize :attr:`output` at init
        and whenever :meth:`defaults` is called
        (when *Defaults* or *Cancel* button is clicked).
        """

        self.output = {}
        """Output dictionary storing user input from  all fields contained
        in the sheets.
        """
        self.output.update(self.default)

        # remove any tabs initially present (2 placeholder tabs added in
        # TabSheets)
        ntabs = self.tabWidget.count()
        for i in range(ntabs):
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.removeTab(self.tabWidget.currentIndex())

        # Add sheets specified in parameters
        for sheet in sheets:
            name = sheet['notetitle']
            a = FieldSheet(fields=sheet['fields'])
            self.sheets[name] = a
            a.setdefaults(self.default)
            self.tabWidget.addTab(self.sheets[name], str(name))
            if QTVERSION < '4.2.0':
                i = self.tabWidget.indexOf(self.sheets[name])
                self.tabWidget.setCurrentIndex(i)
            else:
                self.tabWidget.setCurrentWidget(self.sheets[name])

        # perform the binding to the buttons
        self.buttonOk.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)
        if not nodefaults:
            self.buttonDefaults.clicked.connect(self.defaults)
        if not nohelp:
            self.buttonHelp.clicked.connect(self.myhelp)

    def accept(self):
        """When *OK* is clicked, update :attr:`output` with data from
        :attr:`sheets` (user input)"""
        self.output.update(self.default)
        for _, sheet in self.sheets.items():
            self.output.update(sheet.get())

        # avoid pathological None cases
        for key in list(self.output.keys()):
            if self.output[key] is None:
                if key in self.default:
                    self.output[key] = self.default[key]
        super(QScriptOption, self).accept()

    def reject(self):
        """When *Cancel is clicked, reinitialize :attr:`output` and quit
        """
        self.defaults()
        super(QScriptOption, self).reject()

    def defaults(self):
        """Reinitialize :attr:`output` with :attr:`default`
        """
        self.output = {}
        self.output.update(self.default)

    def myhelp(self):
        """Print help to standard output when the *Help* button is clicked.
        """
        print("Default - Sets back to the initial parameters")
        print("Cancel  - Sets back to the initial parameters and quits")
        print("OK      - Updates the parameters and quits")


class FieldSheet(qt.QWidget):
    """Container widget displaying a variable number of interactive field
    widgets (:class:`MyLabel`,:class:`MyEntryField` or:class:`MyCheckField`)
    in a vertical layout.
    """
    def __init__(self, parent=None, fields=()):
        """

        :param parent: Parent widget
        :param fields: Sequence of sequences defining field widgets. Each
            field is defined by length 3 sequence::

               [field_type, keys, text]

            ``field_type`` can be *"Label", "CheckField", or "EntryField"*

            ``keys`` is a sequences of keys or a single key identifying
             items in the field's internal dictionary.

             ``text`` is the text displayed in a label in the field widget

             If the fied definition sequence is of length 2, it is considered
             to be ``[field_type, text]``. This is only relevant to *Label*
             fields which are not interactive and whose ``getvalue()`` method
             returns an empty dictionary.
        """
        qt.QWidget.__init__(self, parent)
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # self.fields = ([,,,])
        self.fields = []
        self.nbfield = 1
        for field in fields:
            fieldtype = field[0]
            key = field[1] if len(field) == 3 else None
            text = field[-1]

            myfield = None
            if fieldtype == "Label":
                myfield = MyLabel(self, keys=key, text=text)
            elif fieldtype == "CheckField":
                myfield = MyCheckField(self, keys=key, text=text)
            elif fieldtype == "EntryField":
                myfield = MyEntryField(self, keys=key, text=text)
            # elif fieldtype == "RadioField":
            #     myfield = RadioField(self, keys=key, params=parameters)

            if myfield is not None:
                self.fields.append(myfield)
                layout.addWidget(myfield)

    def get(self):
        """Return an agglomerated dictionary with all values stored in all the
        fields internal dictionaries.
        """
        result = {}
        for field in self.fields:
            result.update(field.getvalue())
        return result

    def setdefaults(self, default_dict):
        """Set all fields with values from a dictionary.

        :param default_dict: Dictionary of values to be updated in fields with
            matching keys.
        """
        for field in self.fields:
            field.setdefaults(default_dict)


class Label(qt.QWidget):
    """Simple text label inside a QWidget

    :attr:`TextLabel` is the QLabel widget"""
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.resize(373, 44)

        textfieldlayout = qt.QHBoxLayout(self)
        layout2 = qt.QHBoxLayout(None)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setSpacing(6)
        spacer = qt.QSpacerItem(20, 20,
                                qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        layout2.addItem(spacer)

        self.TextLabel = qt.QLabel(self)

        self.TextLabel.setText(str("TextLabel"))
        layout2.addWidget(self.TextLabel)
        spacer_2 = qt.QSpacerItem(20, 20,
                                  qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        layout2.addItem(spacer_2)
        textfieldlayout.addLayout(layout2)


class MyLabel(Label):
    """Simple label with dummy methods to conform to the interface required
    by :class:`FieldSheet`"""
    def __init__(self, parent=None,
                 keys=(), text=None):  # noqa
        Label.__init__(self, parent)
        if text is not None:
            self.TextLabel.setText(text)

    def getvalue(self):
        """return empty dict"""
        return {}

    def setvalue(self):
        """pass"""
        pass

    def setdefaults(self, default_dict):  # noqa
        """pass"""
        pass


class EntryField(qt.QWidget):
    """Entry field with a QLineEdit (:attr:`Entry`) and a QLabel
    (:attr:`TextLabel`)"""
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        layout1 = qt.QHBoxLayout(self)

        self.TextLabel = qt.QLabel(self)
        self.TextLabel.setText("TextLabel")

        self.Entry = qt.QLineEdit(self)
        layout1.addWidget(self.TextLabel)
        layout1.addWidget(self.Entry)


class MyEntryField(EntryField):
    """Entry field with a QLineEdit (:attr:`Entry`), a QLabel
    (:attr:`TextLabel`), and 3 methods to interact with
    :class:`FieldSheet`: :meth:`getvalue`, :meth:`setvalue` and
    :meth:`setdefaults`

    These methods can be used to get or set the internal dictionary
    storing user input from the entry field."""

    def __init__(self, parent=None,
                 keys=(), text=None):
        """

        :param parent: Parent widget
        :param keys: Keys of :attr:`internal_dict`
        :param text: Text to be displayed in the label.
        """
        EntryField.__init__(self, parent)
        self.internal_dict = {}
        """Dictionary storing user input"""
        if type(keys) == _tuple_type:
            for key in keys:
                self.internal_dict[key] = None
        else:
            self.internal_dict[keys] = None
        if text is not None:
            self.TextLabel.setText(text)
        self.Entry.textChanged[str].connect(self.setvalue)

    def getvalue(self):
        """Return :attr:`internal_dict`"""
        return self.internal_dict

    def setvalue(self, value):
        """Update all values in :attr:`internal_dict` with ``value``"""
        for key in self.internal_dict.keys():
            self.internal_dict[key] = str(value)

    def setdefaults(self, default_dict):
        """Update values in :attr:`internal_dict` with values in
        ``default_dict`` if keys match, then update the entry
        value with each value."""
        for key in list(self.internal_dict.keys()):
            if key in default_dict:
                self.internal_dict[key] = default_dict[key]
                # This will probably trigger setvalue which updates all
                # values to the same value, so at the end I expect all
                # values to be equal to the las one. Do we really want this?
                self.Entry.setText(str(default_dict[key]))


class CheckField(qt.QWidget):
    """Check field with a QCheckBox (:attr:`CheckBox`) """
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.resize(321, 45)

        checkfieldlayout = qt.QHBoxLayout(self)
        checkfieldlayout.setContentsMargins(11, 11, 11, 11)
        checkfieldlayout.setSpacing(6)

        self.CheckBox = qt.QCheckBox(self)
        self.CheckBox.setText("CheckBox")
        checkfieldlayout.addWidget(self.CheckBox)


class MyCheckField(CheckField):
    """Check field with a QCheckBox (:attr:`CheckBox`) and 3 methods to
    interact with :class:`FieldSheet`: :meth:`getvalue`, :meth:`setvalue` and
    :meth:`setdefaults`

    These methods can be used to get or set the internal dictionary
    storing user input from the entry field."""
    def __init__(self, parent=None,
                 keys=(), text=None):
        """

        :param parent: Parent widget
        :param keys: Keys of :attr:`internal_dict`
        :param text: Text to be displayed in the label.
        """
        CheckField.__init__(self, parent)
        self.internal_dict = {}
        """Dictionary storing user input"""
        if type(keys) == _tuple_type:
            for key in keys:
                self.internal_dict[key] = 0
        else:
            self.internal_dict[keys] = 0
        if text is not None:
            self.CheckBox.setText(text)
        self.CheckBox.stateChanged[int].connect(self.setvalue)

    def getvalue(self):
        """Return :attr:`internal_dict`"""
        return self.internal_dict

    def setvalue(self, value):
        """Update all values in :attr:`internal_dict` with 0 if the checkbox
        has been un-ticked or 1 if it has been ticked"""
        if value:
            val = 1
        else:
            val = 0
        for key in self.internal_dict.keys():
            self.internal_dict[key] = val

    def setdefaults(self, default_dict):
        """Update values in :attr:`internal_dict` with values in
        ``ddict`` if keys match, then update the checkbox
        with each value.

        :param default_dict: Dictionary whose values must be integers
            or convertible to integers. All values which don't
            convert to zero will result in the corresponding key
            being set to 1 in :attr:`internal_dict`"""
        for key in self.internal_dict.keys():
            if key in default_dict:
                if int(default_dict[key]):
                    self.CheckBox.setChecked(1)
                    self.internal_dict[key] = 1
                else:
                    self.CheckBox.setChecked(0)
                    self.internal_dict[key] = 0
#
# # FIXME: deactivated, does not work (pyqt3?)
# class RadioField(qt.QWidget):
#     def __init__(self,parent = None,
#                  keys=(), params = ()):
#             qt.QWidget.__init__(self,parent)
#             RadioFieldLayout = qt.QHBoxLayout(self)
#             RadioFieldLayout.setContentsMargins(11, 11, 11, 11)
#             RadioFieldLayout.setSpacing(6)
#
#             self.RadioFieldBox = qt.QButtonGroup(self)
#             self.RadioFieldBox.setColumnLayout(0,qt.Qt.Vertical)
#             self.RadioFieldBox.layout().setSpacing(6)
#             self.RadioFieldBox.layout().setContentsMargins(11, 11, 11, 11)
#             RadioFieldBoxLayout = qt.QVBoxLayout(self.RadioFieldBox.layout())
#             RadioFieldBoxLayout.setAlignment(qt.Qt.AlignTop)
#             Layout1 = qt.QVBoxLayout(None, 0, 6, "Layout1")
#
#             self.internal_dict={}
#             if type(keys) == _tuple_type:
#                 for key in keys:
#                     self.internal_dict[key]=1
#             else:
#                 self.internal_dict[keys]=1
#             self.RadioButton=[]
#             i=0
#             for text in params:
#                 self.RadioButton.append(qt.QRadioButton(self.RadioFieldBox,
#                                                         "RadioButton"+"%d" % i))
#                 self.RadioButton[-1].setSizePolicy(qt.QSizePolicy(1,1,0,0,
#                                 self.RadioButton[-1].sizePolicy().hasHeightForWidth()))
#                 self.RadioButton[-1].setText(str(text))
#                 Layout1.addWidget(self.RadioButton[-1])
#                 i=i+1
#
#             RadioFieldBoxLayout.addLayout(Layout1)
#             RadioFieldLayout.addWidget(self.RadioFieldBox)
#             self.RadioButton[0].setChecked(1)
#             self.RadioFieldBox.clicked[int].connect(self.setvalue)
#
#     def getvalue(self):
#         return self.internal_dict
#
#     def setvalue(self,value):
#         if value:
#             val=1
#         else:
#             val=0
#         for key in self.internal_dict.keys():
#             self.internal_dict[key]=val
#         return
#
#     def setdefaults(self, ddict):
#         for key in list(self.internal_dict.keys()):
#             if key in ddict:
#                 self.internal_dict[key]=ddict[key]
#                 i=int(ddict[key])
#                 self.RadioButton[i].setChecked(1)
#         return


def test():
    a = qt.QApplication(sys.argv)
    w1 = FieldSheet(fields=(["Label", 'Dummy FieldSheet Widget'],
                            ["EntryField", 'entry', 'MyLabel'],
                            ["CheckField", 'label', 'Check Label'],))
                            # ["RadioField",'radio',('Button1','hmmm','3')]))
    w1.show()
    sheet1 = {'notetitle': "First Sheet",
              'fields': (["Label", 'label on first page'],
                         ["EntryField", 'entry', 'MyLabel'],
                         ["CheckField", 'label', 'Check Label'])}
    sheet2 = {'notetitle': "Second Sheet",
              'fields': (["Label", 'bépo'],
                         ["EntryField", 'entry2', 'MyLabel2'],
                         ["CheckField", 'label2', 'Check Label2'],
                         ["EntryField", 'entry3', 'MyLabel3'],
                         ["CheckField", 'label3', 'Check Label3'])}
    w2 = QScriptOption(name='QScriptOptions', sheets=(sheet1, sheet2),
                      default={'entry': 'type here', 'label': 1, "label3": 0,
                               'entry3': "sanglots longs des violons"})

    w2.show()
    a.exec_()
    print(w2.output)

if __name__ == "__main__":
    test()
