import sys
import re


def check_transcript(source_file, present_default_day=100, grade_boundry=70):
    '''present_default_day: 預設的應出席日數
    grade_boundry: 最低的正常分數
    '''
    output = []

    with open(source_file) as fp:
        transcript_content = fp.read()

    # 應出席日數的 flag，如果全班都是一樣的數字，代表老師可能忘記改
    present_ok_status = {}
    
    students_html = re.findall(r'^<div width="649".+?<div id=\'div999_\d+\'', transcript_content, re.DOTALL|re.MULTILINE)
    for student_html in students_html:
        present_day = None
        m = re.search(r"alle-wordpicker-font-family-kai' >(.+?)</TH>", student_html)
        if m:
            stu_name = m.group(1).replace('\u3000', ' ')
            class_name = stu_name.split()[0]
            if class_name not in present_ok_status:
                present_ok_status[class_name] = False
        else:
            raise Exception('oops')

        # 檢查學業等第有無漏填，用負向表列檢查
        grade_ok = True
        if 'valign="middle">--</TD>' in student_html:
            grade_ok = False
            output.append('{stu_name} 有未填的學業等第'.format(stu_name=stu_name))
        
        # 檢查行為表現情形有無空白
        m = re.search(r'日常行為表現、團體活動表現、公共服務、校內外特殊表現</th>\s+<td align="left" valign="top"> &nbsp;</td>', student_html, re.DOTALL)
        if m:
            output.append('{stu_name} 有未填的行為表現情形'.format(stu_name=stu_name))

        # 檢查是否有勾選具體目標
        m = re.findall(r'<TR><TD style="border:1px solid" width="60%">.+?</TR>', student_html, re.DOTALL)
        for each_tr in m:
            if 'Ｖ' not in each_tr:
                output.append('{stu_name} 有未填的學習目標'.format(stu_name=stu_name))
        
        # 檢查導師總結性評語及具體建議是否為空
        m = re.search(r'導師總結性評語及具體建議（包括學生日常生活表現評量及學習領域評量）</span></TD></TR>.+?<TR><TD width="96%" align="left" valign="top" ><span class="txt_15">&nbsp;</span></TD></TR>', student_html, re.DOTALL)
        if m:
            output.append('{stu_name} 有未填的導師總結性評語及具體建議'.format(stu_name=stu_name))
        
        # 檢查學生的實際出席日數，只要有一位學生的日數不同於 present_default_day，就當作老師有記得改，否則應該是忘記改
        m = re.search(r'抗力</td>.+?<tr>.+?<th height="40" align="center" scope="row">\d+</th>.+?<td align="center">.+?</td>.+?<td align="center">(.+?)</td>', student_html, re.DOTALL)
        try:
            if int(m.group(1)) != present_default_day:
                present_ok_status[class_name] = True
        except ValueError:
            # 一天請假算 8 節，若日數出現小數點，代表老師搞錯，可能一天算成 7 節之類
            output.append('{stu_name} 實際出席日數 {present_day} 異常，應為整數'.format(stu_name=stu_name, present_day=m.group(1)))
        
        # 檢查學生的各科分數是否低於門檻
        m = re.findall(r'<TH width="15%" style="border:1px solid ; border-left:2px solid" align="center" valign="top" scope=row>(.+?)</TH>.+?<TD width="6%" style="border:1px solid ; border-right:2px solid" align="center" align=center valign="middle">(\d+)</TD>', student_html, re.DOTALL)
        if m and grade_ok:
            for each_subject in m:
                if int(each_subject[1]) < grade_boundry:
                    output.append('{stu_name} 的 {subject} 分數 {grade} 低於 70'.format(stu_name=stu_name, subject=each_subject[0], grade=each_subject[1]))
    
    # 檢查實際出席有問題的班級
    for each_class in present_ok_status:
        if present_ok_status[each_class] == False:
            output.append('{each_class}全班同學實際出席日數相同，請確認老師有修改此欄位'.format(each_class=each_class))

    return '\n'.join(output)


if __name__ == '__main__':
    source_file = sys.argv[1]
    output = check_transcript(source_file)
    print(output)
