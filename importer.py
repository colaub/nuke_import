# python built-in imports
import os
import re
import shutil
import getpass

# PySide specific imports
from PySide2 import QtWidgets, QtCore, QtGui

# Software specific import
import nuke


def get_project():
    """
    get project path for each group

    :return: project path
    :rtype: string
    """
    user = getpass.getuser()
    project_path = "C:/Users/{}/Documents/maya/2018/prefs/mega_tuyau_settings/project_path.mega".format(user)
    with open(project_path) as data:
        path = os.path.normpath(data.read())
    return path


class Importer(QtWidgets.QDialog):
    """Create UI and populate it"""

    def __init__(self):
        super(Importer, self).__init__()
        self.num_count = 1
        
        # setting the path directory
        path = nuke.root().name()
        path = path.split('/')
        path_directory = os.path.join(main_path # sort d'ou main_path ?,
                                      'render',
                                      'shots',
                                      path[-4],
                                      path[-3]) # c'est pas tres beau de faire du split de chemins comme ca mais ca c'est pas ta faute. 
        self.HD_path = os.path.join(path_directory, 'HD')
        self.LD_path = os.path.join(path_directory, 'LD')
        self.FML_path = os.path.join(path_directory, 'FML')

        self.setWindowTitle('Import File')
        self.build_ui()
        self.start_quality()
        self.pass_populate()

    def build_ui(self):
        """UI Creation"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)

        data_widget = QtWidgets.QWidget()
        data_widget.setFixedWidth(270)
        data_layout = QtWidgets.QVBoxLayout(data_widget)
        data_layout.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(data_widget)

        version_widget = QtWidgets.QWidget()
        version_layout = QtWidgets.QHBoxLayout(version_widget)
        version_layout.setContentsMargins(0, 0, 0, 0)
        version_layout.setAlignment(QtCore.Qt.AlignCenter)
        data_layout.addWidget(version_widget)

        self.version_drop_down = QtWidgets.QComboBox()
        self.version_drop_down.setMinimumWidth(100)
        version_layout.addWidget(self.version_drop_down)

        self.ld_checkbox = QtWidgets.QCheckBox()
        self.ld_checkbox.setChecked(0)
        version_layout.addWidget(self.ld_checkbox)
        
        self.ld_label = QtWidgets.QLabel('Show LD')
        version_layout.addWidget(self.ld_label)

        self.fml_checkbox = QtWidgets.QCheckBox()
        self.fml_checkbox.setChecked(0)
        version_layout.addWidget(self.fml_checkbox)
        
        self.fml_label = QtWidgets.QLabel('Show FML')
        version_layout.addWidget(self.fml_label)

        path_label = QtWidgets.QLabel('Avaible Pass')
        path_label.setStyleSheet(
            "background-color: #5d5d5d;border: 3px solid #5d5d5d;border-radius: 3px;boldLabelFont;")
        path_label.setFont(QtGui.QFont('boldLabelFont', 8, QtGui.QFont.Bold))
        data_layout.addWidget(path_label)

        self.path_tree = QtWidgets.QTreeWidget()
        self.path_tree.setHeaderHidden(True)
        self.path_tree.setIconSize(QtCore.QSize(100, 100))
        self.path_tree.setStyleSheet("QTreeWidget::item{padding: 5px 0;}")
        self.path_tree.setFont(QtGui.QFont('Liberation Mono'))
        self.path_tree.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        data_layout.addWidget(self.path_tree)

        nbr_widget = QtWidgets.QWidget()
        nbr_layout = QtWidgets.QHBoxLayout(nbr_widget)
        nbr_layout.setAlignment(QtCore.Qt.AlignLeft)
        nbr_layout.setContentsMargins(3, 3, 3, 3)
        nbr_layout.setAlignment(QtCore.Qt.AlignLeft)
        data_layout.addWidget(nbr_widget)

        ### bordel ici, pourquoi tu saute une ligne a chaque fois, fait des blocs d'interet comme j'ai fait au dessus. 
        self.ref_label = QtWidgets.QLabel('Work on local')

        self.pass_drop_down_label = QtWidgets.QLabel('All pass from ')

        self.checkbox = QtWidgets.QCheckBox()

        self.pass_drop_down = QtWidgets.QComboBox()

        self.checkbox.setChecked(1)

        nbr_layout.addWidget(self.checkbox)
        nbr_layout.addWidget(self.ref_label)

        nbr_layout.setAlignment(QtCore.Qt.AlignLeft)

        passes_widget = QtWidgets.QWidget()

        passes_layout = QtWidgets.QHBoxLayout(passes_widget)
        passes_layout.setAlignment(QtCore.Qt.AlignLeft)
        passes_layout.setContentsMargins(3, 3, 3, 3)

        data_layout.addWidget(passes_widget)

        self.pass_drop_down_label = QtWidgets.QLabel('Import all passes from')

        self.pass_drop_down_label2 = QtWidgets.QLabel('All pass from ')

        self.checkbox_passes = QtWidgets.QCheckBox()

        self.pass_drop_down = QtWidgets.QComboBox()

        passes_layout.addWidget(self.checkbox_passes)
        passes_layout.addWidget(self.pass_drop_down_label)
        passes_layout.addWidget(self.pass_drop_down)

        self.import_button = QtWidgets.QPushButton('Import')

        data_layout.addWidget(self.import_button)
        #### fin

        self.fml_checkbox.clicked.connect(self.fml)
        self.ld_checkbox.clicked.connect(self.ld)
        self.import_button.clicked.connect(self.import_fct)
        self.ld_checkbox.stateChanged.connect(self.get_version)
        self.ld_checkbox.stateChanged.connect(self.pass_populate)
        self.version_drop_down.activated.connect(self.pass_populate)
        self.get_version() # bloc reserve au singaux pourquoi y a ca la ????
        self.fml_checkbox.stateChanged.connect(self.get_version)
        self.fml_checkbox.stateChanged.connect(self.pass_populate)

    def fml(self):
        """uncheck ld button if fml is check"""
        self.ld_checkbox.setChecked(0) # si je comprend bien on pourra jamais checked la check box manuellement

    def ld(self):
        """uncheck fml button if ld is check"""
        self.fml_checkbox.setChecked(0) # si je comprend bien on pourra jamais checked la check box manuellement

    def start_quality(self):
        """
        chose first quality to be shown
        If there is no HD render it shows the LD if no LD it shows
        FML else return no render found
        """
        if not os.path.exists(self.HD_path):
            if os.path.exists(self.LD_path):
                self.ld_checkbox.setChecked(1)
            else:
                print("no LD render found")
            if os.path.exists(self.FML_path):
                self.fml_checkbox.setChecked(1)
            else:
                print("no FML render found")

    def last_version(self, path):
        """get and set last version

        :param: path(str): path depending on quality
        """
        version_list = sorted(os.listdir(path), reverse=True)
        self.version_drop_down.clear()
        self.version_drop_down.addItems(version_list)

    def get_version(self):
        """get render last version by quality"""
        print(self.LD_path) # print util ?
        if os.path.exists(self.HD_path):
            self.last_version(self.HD_path)
        if self.ld_checkbox.isChecked() and os.path.exists(self.LD_path):
            self.last_version(self.LD_path)
        if self.fml_checkbox.isChecked() and os.path.exists(self.FML_path):
            self.last_version(self.FML_path)

    def pass_populate(self):
        """show all the pass in the UI"""
        self.parentitem = {}
        self.pass_drop_down.clear()
        self.pass_drop_down.addItem('All layers')
        self.path_tree.clear()

        # choose which quality to display
        # redondant avec start quality ???
        path_directory = self.HD_path
        if not os.path.exists(self.HD_path):
            path_directory = self.LD_path
            if not os.path.exists(path_directory):
                path_directory = self.FML_path
            else:
                print('no render for this shot')
        if self.ld_checkbox.isChecked():
            path_directory = self.LD_path
        if self.fml_checkbox.isChecked():
            path_directory = self.FML_path
        version = self.version_drop_down.currentText()
        path_version = os.path.join(path_directory, version)
        path_list = os.listdir(path_version)
        ### fin 
        
        # get all pass and add them
        for category in path_list:
            path_name_list = []
            item_type = QtWidgets.QTreeWidgetItem(category)
            item_type.setText(0, category)
            item_type.setFlags(QtCore.Qt.ItemIsEnabled)
            self.parentitem[category] = item_type
            all_path_directory = os.path.join(path_version, category)
            if os.listdir(all_path_directory):
                self.pass_drop_down.addItem(category)
            paths = os.listdir(all_path_directory)
            for path in paths:
                if 'ID' in path.upper():
                    path_name = path.split('_')
                    path_name = path_name[-3] + '_' + path_name[-2]
                else:
                    path_name = path.split('_')
                    path_name = path_name[-2]
                if path_name not in path_name_list:
                    path_name_list.append(path_name)
            for item in path_name_list:
                path_item = QtWidgets.QTreeWidgetItem(item)
                item_type.addChild(path_item)
                path_item.setText(0, item)
                self.path_tree.addTopLevelItem(item_type)

    # soit une def non membre de la class, soit une @staticmethod
    def count_files(self, path):
        """
        Count the number of file to copy on local

        :param: path(str): dir in which count the file
        :return: number of file
        :rtype: (int)
        """
        files = []
        if os.path.isdir(path):
            for path, dirs, filename in os.walk(path):
                files.extend(filename)
        return len(files)

    # soit une def non membre de la class, soit une @staticmethod
    def makedirs(self, dest):
        """
        Create the directory that will contain the files

        :param: dest(str): path where to create the directory
        """
        if not os.path.exists(dest):
            os.makedirs(dest)

    # soit une def non membre de la class, soit une @staticmethod
    def copyfile(self, src, dest):
        """
        copy the files

        :param: src(str): source path
        :param: dest(str): destination path
        """
        if not os.path.isfile(dest):
            shutil.copy(src, dest)
        else:
            os.remove(dest)
            shutil.copy(src, dest)
            
    def copy_files_with_progress(self, src, dest, name):
        """
        update the loading bar for each file copied

        :param: src(str): source path
        :param: dest(str): destination path
        :param: name(str): str that the file must contain to be copied
        """
        num_files = self.count_files(src)
        if num_files == 0:
            return
        self.makedirs(dest)
        num_copied = 0
        for path, dirs, filenames in os.walk(src):
            for directory in dirs:
                dest_dir = path.replace(src, dest)
                self.makedirs(os.path.join(dest_dir, directory))
        sfiles = []
        for sfile in filenames:
            QtWidgets.QApplication.processEvents()
            if name in sfile:
                src_file = os.path.join(path, sfile)
                dest_file = os.path.join(path.replace(src, dest), sfile)
                sfiles.append((src_file, dest_file))
        self.num_count = len(sfiles)
        for src, dst in sfiles:
            shutil.copy(src, dst)
            num_copied += 1
            progress = int(num_copied / float(self.num_count) * 100)
            QtWidgets.QApplication.processEvents()
            self.progress.setValue(progress)

    def import_fct(self):
        """
        main fonction

        it'll copy, import, rename and set correctly all the file in nuke
        """
        self.progressWindow = QtWidgets.QDialog()
        self.progress = QtWidgets.QProgressBar(self)
        layout = QtWidgets.QHBoxLayout(self.progressWindow)
        layout.addWidget(self.progress)
        self.progressWindow.show()

        # define the proxy folder
        proxy_path = 'D:/TEMP_NUKE'
        dic_frame = {}
        path = nuke.root().name()
        path = path.split('/')
        path_directory = self.HD_path
        version = self.version_drop_down.currentText()
        selected = self.path_tree.selectedItems()
        
        # create proxy folder
        proxy_path = os.path.join(proxy_path,
                                  path[-4],
                                  path[-3])

        # if the box is check it'will import all pass of a layer or all layer
        if self.checkbox_passes.isChecked():
            child_list = []
            # get layers
            layer = self.pass_drop_down.currentText()
            if layer in self.parentitem:
                layer_sel = self.parentitem[layer]
                layer_sel.setSelected(True)
                count = layer_sel.childCount()
                for i in range(count):
                    child = layer_sel.child(i)
                    child_list.append(child)
                    selected = child_list
            if layer == 'All layers':
                for key, value in self.parentitem.iteritems():
                    value.setSelected(True)
                    count = value.childCount()
                    for i in range(count):
                        child = value.child(i)
                        child_list.append(child)
                        selected = child_list

        # import by selected pass
        for i in selected:
            selected = i.text(0)
            qual = 'HD'
            if self.ld_checkbox.isChecked():
                path_directory = self.LD_path
                qual = 'LD'
            elif self.fml_checkbox.isChecked():
                path_directory = self.FML_path
                qual = 'FML'
            if QtWidgets.QTreeWidgetItem.parent(i):
                pass_type = QtWidgets.QTreeWidgetItem.parent(i)
                pass_type = pass_type.text(0)
                path_path = os.path.abspath(os.path.join(path_directory,
                                                         version,
                                                         pass_type))
                all_frame_list = os.listdir(path_path)
                selectedlist = []
                for frame in all_frame_list:
                    name_frame = frame[:-9] + '_'
                    if '_' + selected in name_frame:
                        frame_nbr = frame[-8:]
                        frame_nbr = frame_nbr[:-4]
                        selectedlist.append(int(frame_nbr))
                        selectedlist = sorted(selectedlist)
                        end = selectedlist[-1]
                        first = selectedlist[0]
                        start_end = [first, end]
                        dic_frame = {name_frame: start_end}

                # create the path
                for key, value in dic_frame.items():
                    self.progress.setValue(0)
                    new_path = (os.path.abspath("{}/{}####.exr {}-{}".format(
                        path_path, key, value[0], value[1]))).replace("\\", "/")
                    main_path = (os.path.abspath("{}/{}####.exr".format(path_path, key))).replace("\\", "/")
                    proxy = os.path.join(proxy_path,
                                         qual)
                    proxycoucou = proxy
                    new_proxy_path = "{}/{}####.exr {}-{}".format(
                        proxy, key, value[0], value[1])
                    name = pass_type + '_' + selected

                    # if the node already exist just update the path
                    if nuke.exists(name):
                        node = nuke.toNode(name)
                        node.knob('file').fromUserText(os.path.abspath(new_path))
                        if self.checkbox.isChecked():
                            self.progressWindow.setWindowTitle(selected)
                            self.copy_files_with_progress(
                                path_path, proxycoucou, key)
                            node.knob('proxy').fromUserText(
                                os.path.normpath(new_proxy_path))
                    # else create the node
                    else:
                        print(new_path)
                        readNode = nuke.nodes.Read(file=main_path, first=value[0], last=value[1], name=name)
                        node = nuke.toNode(name)
                        if self.checkbox.isChecked():
                            self.progressWindow.setWindowTitle(selected)
                            self.copy_files_with_progress(
                                path_path, proxycoucou, key)
                            # self.progressWindow.close()
                            node.knob('proxy').fromUserText(
                                os.path.normpath(new_proxy_path))
        self.progressWindow.close()

        # auto create Deep EXRID network
        if nuke.exists('ALL_ALL_ExrID'):
            value = nuke.toNode('ALL_ALL_ExrID').knob('file').getValue()
            value = value.replace('%04d', '####')
            first = nuke.toNode('ALL_ALL_ExrID').knob('first').getValue()
            last = nuke.toNode('ALL_ALL_ExrID').knob('last').getValue()
            value = value + ' {}-{}'.format(int(first), int(last))
            infopath = nuke.root().name()
            infopath = infopath.split('/')
            nodename = infopath[-4] + '_' + infopath[-3] + '_DeepRead'
            if nuke.exists(nodename):
                print('exist')
                my_node = nuke.toNode(nodename)
            else:
                my_node = nuke.createNode('DeepRead')
                my_node.setName(nodename)
                my_node.knob('on_error').setValue(3)
            my_node.knob('file').fromUserText(value)
            
            open_exrid = nodename.replace('DeepRead', 'OpenEXRId')
            if nuke.exists(open_exrid):
                print('exist')
                key = nuke.toNode(open_exrid)
            else:
                key = nuke.createNode('DeepOpenEXRId')
                key.setName(open_exrid)
            key.setInput(0, my_node)

            deeptoimage = nodename.replace('DeepRead', 'DeepToImage')
            if nuke.exists(deeptoimage):
                print('exist')
                value = nuke.toNode(deeptoimage)
            else:
                value = nuke.createNode('DeepToImage')
                value.setName(deeptoimage)
            value.setInput(0, key)
            exr_pass = nuke.toNode('ALL_ALL_ExrID')
            nuke.delete(exr_pass)

            
def show_ui():
    """Init UI"""
    ui = Importer()
    ui.show()
    return ui


p = re.compile("[0-9]{4}_[0-9]{4}_Comp.nk$")

if not p.match(nuke.root().name().split('/')[-1]):
    nuke.message('open a valid comp file please')
else:
    main_path = get_project()
    ui = Importer()
    ui.show()
