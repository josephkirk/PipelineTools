


                    # with columnLayout():
                    #     with frameLayout(label='Bone Rename', collapsable=False):
                    #         with rowColumnLayout(
                    #             numberOfColumns=7,
                    #             columnWidth=[
                    #                 (1,200),
                    #                 (2,60),
                    #                 (3,40),]):
                    #             self.ui['renameBone']=[]
                    #             self.ui['renameBone'].append(textField())
                    #             self.ui['renameBone'].append(optionMenu())
                    #             with self.ui['renameBone'][1]:
                    #                 menuItem(label='')
                    #                 menuItem(label='Front')
                    #                 menuItem(label='Left')
                    #                 menuItem(label='Right')
                    #                 menuItem(label='Center')
                    #                 menuItem(label='Back')
                    #                 menuItem(label='Middle')
                    #             self.ui['renameBone'].append(intField(value=0))
                    #             self.ui['renameBone'].append(intField(value=1))
                    #             self.ui['renameBone'].append(textField(text='bon'))
                    #             button(
                    #                 label='Rename',
                    #                 c=lambda x:ru.rename_bone_Chain(
                    #                             self.ui['renameBone'][0].getText()+self.ui['renameBone'][1].getValue(),
                    #                             self.ui['renameBone'][2].getValue(),
                    #                             self.ui['renameBone'][3].getValue(),
                    #                             self.ui['renameBone'][4].getText(),
                    #                             sl=True))
                    #             button(
                    #                 label='Label',
                    #                 annotation='use joint name as label',
                    #                 c=Callback(ru.label_joint, sl=True))