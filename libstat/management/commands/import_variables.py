# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from libstat.models import Variable, PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY
from xlrd import open_workbook

class Command(BaseCommand):
    args = "<file> [LibraryType]"
    help = "Imports statistical variables from a spreadsheet"
    
    libraryTypes = { "public": PUBLIC_LIBRARY, "research": RESEARCH_LIBRARY, "hospital": HOSPITAL_LIBRARY, "school": SCHOOL_LIBRARY}

    def handle(self, *args, **options):
        if(len(args) != 2):
            self.stdout.write("Usage: python manage.py import_variables <SourceFile> [LibraryType]\n\n")
            self.stdout.write("\tfile: Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx")
            self.stdout.write("\tLibraryType; public, research, hospital, school")
            return
        
        file = args[0]
        library_type = args[1]

        if library_type not in self.libraryTypes.keys():
            self.stdout.write(u"Invalid LibraryType '{}', aborting".format(library_type))
            return
        target_group = self.libraryTypes[library_type]

        self.stdout.write(u"Importing {} variables from: {}".format(target_group, file))

        book = open_workbook(file)
        work_sheet = book.sheet_by_index(0)

        for i in range(1, work_sheet.nrows):
            row = work_sheet.row_values(i)
            
            #Columns: 0-Alias, 1-Description, optional: 2-Comment, 3-Variable
            alias = row[0].strip()
            description = row[1].strip()
            comment = None
            variable = None
            is_public = True
            
            if work_sheet.ncols > 2:
                comment = row[2].strip()
            if work_sheet.ncols > 3:
                variable = row[3].strip()
            if not variable:
                variable = alias
            if comment:
                # Not the best way to determine if a field is private or public, but it's the only one I've got. 
                is_public=False
            
            existing_vars = Variable.objects.filter(key=variable)
            if len(existing_vars) == 0:
                object = Variable(key=variable, alias=alias, description=description, comment=comment, is_public=is_public, target_groups=[target_group])
                object.save()
                self.stdout.write("IMPORTED: key={}, alias={}, is_public={}, target_groups={}".format(object.key, object.alias, object.is_public, object.target_groups))
            else:
                object = existing_vars[0]
                if target_group not in object.target_groups:
                    object.target_groups.append(target_group)
                    object.save()
                    self.stdout.write("UPDATED: Added target_group to {}. target_groups={}".format(object.key, object.target_groups))
                else:
                    self.stdout.write("SKIPPED: {} already exists".format(object.key))
            

