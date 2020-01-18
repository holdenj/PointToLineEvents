import arcpy
import numpy
import sys
import os
import traceback
reload
class EventToolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Winter Trails Python Toolbox"
        self.alias = "Winter Trails Python Toolbox to create Line Events from Point Events"        
        self.tools = [EventTableTool]        # List of tool classes associated with this toolbox
class EventTableTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""        
        self.label = "Create Line Event Table from Points"
        self.description = "Creates a Line event Table from a set of points."
        self.canRunInBackground = True
        # self.getParameterInfo
        # self.eventtableName = self.getParameterInfo        
        return
    def getParameterInfo(self):
        """Define parameter definitions"""
        # datatype="GPFeatureLayer", direction = "Input" )
        # DataTypes in ArcMap http://desktop.arcgis.com/en/arcmap/10.3/analyze/creating-tools/defining-parameter-data-types-in-a-python-toolbox.htm
        # DataTypes in ArcGIS Pro https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/defining-parameter-data-types-in-a-python-toolbox.ht
        #
        param0 = arcpy.Parameter(displayName = "Input csv file of Groomer Points", name = "groomerCSV",datatype="DEFile", direction = "Input") #  Response file from C#
        param0.value = r'C:\AtlasTrackExample\API New\Response.csv'        
        param0.filter.list = ['csv','txt']  # Only allow *.csv and *.txt extensions
        param1 = arcpy.Parameter(displayName = "Groomer Locations", name = "groomerLocations",datatype="DEFeatureClass", direction = "input")  #  The output location for the GroomerPoints
        param1.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Groomed_Points\Groomer_Locations'
        param2 = arcpy.Parameter(displayName = "Area of Interest Polygon", name = "routeArea",datatype="DEFeatureClass", direction = "Input")  #  Polygon with the Area of Interest
        param2.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Non_Motorized\RouteArea'
        param2.filter.list = ["Polygon"]
        param3 = arcpy.Parameter(displayName = "Area of Interest Expression", name = "areaOfInterestExpression",datatype="GPSQLExpression", direction = "Input")  #  Expression to restrict the Area of Interest.
        param3.value = "AreaCode = 'I-90 Cabin Creek'"
        param4 = arcpy.Parameter(displayName = "Event Table Name", name = "tableName",datatype="DETable", direction = "Input")
        param4.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\CabinCreekGroomerEvents_Test'
        param5 = arcpy.Parameter(displayName = "Route Feature Class Name", name = "routeName",datatype="DEFeatureClass", direction = "Input" )
        param5.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Non_Motorized\Ski_Routes'
        param5.filter.list = ["Polyline"]
        param6 = arcpy.Parameter(displayName = "Event Layer File", name = "eventLayerFile",datatype="DELayer", direction = "Input" )
        param6.value = r'C:\AtlasTrackExample\Trails\Layers\GroomerEvents.lyr'        
        param6.filter.list = ['lyr']  # Only allow *.lyr extensions
        params =[param0, param1, param2, param3, param4, param5, param6]
        return params
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        # The following variables if true only allows parts of the program to run.  This would assume those parts already exist and have been run.
        displayParameters = False
        loadCSV = True            # True to load a new CSV
        createEvents = True       # True to make events for a new CSV
        addEventLayer = False     # False When an existing Map Document is used.
        saveMXD       = False     # False When an existing Map Document is used.
        # Get the parameters
        self.responseCSV = parameters[0]                # responseCSV = r'C:\AtlasTrackExample\API New\Response.csv'
        self.groomerLocations = parameters[1]            # Groomer "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Groomed_Points\\Groomer_LocationsMultipart"
        self.areaOfInterest = parameters[2]             # areaOfInterest = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Non_Motorized\RouteArea'
        self.areaOfInterestExpression = parameters[3]   # areaOfInterestExpression =  "AreaCode = 'Washington State'"        
        self.eventTableName = parameters[4]             # eventTableName = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Ski_Events        
        self.routeFeatureClassName = parameters[5]      # routeFeatureClassName = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Ski_Routes'
        self.layerFileName = parameters[6]              # layerFileName = r'C:\AtlasTrackExample\Trails\Layers\Ski_Grooming by Day.lyr'
        # Display the Parameters        
        if (displayParameters):
            arcpy.AddMessage('In EventTableTool Execute 0 Response.csv               Parameter is ' + self.responseCSV)
            arcpy.AddMessage('In EventTableTool Execute 1 GroomerLocations           Parameter is ' + self.groomerLocations)
            arcpy.AddMessage('In EventTableTool Execute 2 AreaOfInterest             Parameter is ' + self.areaOfInterest)
            arcpy.AddMessage('In EventTableTool Execute 3 AreaOfInterestExpression   Parameter is ' + self.areaOfInterestExpression)
            arcpy.AddMessage('In EventTableTool Execute 4 Table input                Parameter is ' + self.eventTableName)
            arcpy.AddMessage('In EventTableTool Execute 5 Feature Class              Parameter is ' + self.routeFeatureClassName)
            arcpy.AddMessage('In EventTableTool Execute 6 File Name                  Parameter is ' + self.layerFileName)                
        # Import the groomer points from the CSV File
        if (loadCSV):
            if (arcpy.Exists(self.responseCSV)):
                self.csvFile = CSVFile(self.responseCSV)
                self.csvFile.MakeXYEventLayer(self.groomerLocations)
                arcpy.AddMessage('Created XY Event Layer ' + self.groomerLocations + '.')
            else:
                arcpy.AddMessage(self.responseCSV + ' does not exist.  Check that file in response parameter exists.')
                arcpy.AddMessage('Program PointToLineEvents will exit.')
                exit()       # Exits the program.        
        # Create Route Object
        # routeFeatureClass = Route(routeFeatureClassName)
        self.route = Route(self.routeFeatureClassName)
        self.routeKeyFieldName = 'NAME'
        eventTable = EventTable(self.eventTableName, self.routeFeatureClassName, self.routeKeyFieldName)    # Create the Event Table object with Table Name, route and key field.
        if (createEvents):
            self.routeFieldList = ['NAME','Shape_Length']
            self.routeSortField = 'NAME'        
            self.routeQuery = """OBJECTID > 0"""
            self.routeNameFieldList = ['NAME']
            # self.query = "" + self.fieldName + " = '" + self.fieldValue + "'" 
            # Get a list of routes and their lengths.        
            self.routeList = self.route.SelectFromQuery(self.routeQuery, self.routeFieldList, self.routeSortField)
            self.routeNameList = self.route.SelectFromQuery(self.routeQuery, self.routeNameFieldList, self.routeSortField)
            self.listClass = ListClass(self.routeList)                      # Create the List Last with the self.routeList
            # self.listClass.DisplayList()                                  # Display the List                 Not needed except for testing
            self.trailsList = self.listClass.DisplayTrails()              # Display the Trails List            Still needed except for testing
            # trailsLengthList = self.listClass.DisplayTrailLengths()       # Display the Trails Length List   Not needed except for testing        
            # Calculate fields for the EventTable
            eventTable = EventTable(self.eventTableName, self.routeFeatureClassName, self.routeKeyFieldName)    # Create the Event Table object with Table Name, route and key field.
            self.searchDistance = "100 Feet"        
            eventTable.LocateFeaturesAlongRoutes(self.groomerLocations, self.searchDistance)    # Locate points along the route
            eventTable.AddEventFields()                                                         # Add Fields for line events
            eventTable.CalculateFieldTO_MEAS()                                                  # Calculate To Measures for some events.
            eventTable.CalculateFieldOFFSET()                                                   # Add Offset
            eventTable.CalculateFieldDAYS_AGO()                                                 # Calculate number of days ago
            eventTable.CalculateFieldHOURS_AGO()                                                # Calculate number of hours ago
            self.eventfieldList = ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET','DAYS_AGO','HOURS_AGO']        
            # self.sqlClause = (None,'ORDER BY MEAS')  ## Order may be changed for different effect
            # self.sqlClause = (None,'ORDER BY HOURS_AGO')  ## Order may be changed for different effect
            self.sqlClause = (None,'ORDER BY HOURS_AGO, MEAS')  ## Order may be changed for different effect
            # Order Rows        
            # Calculate FROM_MEAS to be 0 for first, and previous measurement for the others.
            eventTableAllFieldsList = eventTable.GetAllFieldList()
            for trailName in self.trailsList:
                if trailName == None:
                    trailName = "Unnamed"
                    arcpy.AddMessage('Blank Trail name is now ' + trailName)
                else:                
                    # trailName = "Mt. Amabalis"
                    # eventTable.SelectAndOrderRows('NAME',trailName,self.eventfieldList, 'MEAS',self.sqlClause)  # Works but not needed.  Only Lists.                
                    eventTable.CalculateFieldFROM_MEAS('NAME',trailName,self.eventfieldList,'MEAS','FROM_MEAS',self.sqlClause)
                    trailNameIndex = self.routeNameList.index([trailName])  # Look for the array for the trailName
                    trailLength = self.routeList[trailNameIndex][1]         # Length of the trail
                    arcpy.AddMessage('Trail name  ' + trailName + ' is ' + str(trailLength) + ' feet long.')
                    eventTable.AddRecordsAfterGroomerPoint('NAME',trailName,eventTableAllFieldsList,'MEAS','FROM_MEAS',self.sqlClause, trailLength)
        if (addEventLayer):
            # Create and Add the Event Layer        
            eventTable.AddEventLayer(self.routeFeatureClassName, self.eventTableName, self.layerFileName)        
        if (saveMXD):
            try:   # Map Document 
                mapDocument = arcpy.mapping.MapDocument('CURRENT')
                mapDocumentFile = mapDocument.filePath
                self.current = True
            except:
                mapDocumentFile = r'C:\AtlasTrackExample\Trails\ArcMap\WinterTrails.mxd'
                self.current = False
            if (len(mapDocumentFile)>0):                       # If there is a map document
                mapDocument = MapDocument(mapDocumentFile)     # Create MapDocument object
                mapDocument.AddLayerToMap(self.layerFileName)  # Add a layer layerFileName  =  r'C:\AtlasTrackExample\Trails\Layers\Ski Grooming by Day.lyr'
                arcpy.AddMessage('EventTableTool execute  Added Layer File ' + self.layerFileName)
            if (self.current):
                pass
                # mapDocumentCopyFile = r'C:\AtlasTrackExample\Trails\ArcMap\WinterTrails_new.mxd'
                # mapDocument.SaveMapDocumentCopy()            
            else:
                mapDocument.SaveMapDocument()
        arcpy.AddMessage('EventTableTool execute method completed.  Event table ' + self.eventTableName + ' has been created.')
        arcpy.AddMessage('***************************************************************************************************')
        return
class Table(object):
    def __init__(self, tableName):
        self.tableName = tableName
        self.allFieldsList = arcpy.ListFields(self.tableName)
        if arcpy.Exists(self.tableName):
            self.tableName = tableName                        
            arcpy.AddMessage('In Table Class __init__ ' + self.tableName + ' exists.')
            arcpy.RefreshCatalog(self.tableName)  # Refreshed the Table so that it see the latest structure.
        else:
            arcpy.AddError('In Table Class __init__ ' + self.tableName + ' does not exist.')
        return
    def FieldExists(self, FieldName):
        self.fieldName = FieldName
        if len(arcpy.ListFields(self.tableName,self.fieldName))>0:
             arcpy.AddMessage(self.fieldName + ' already exits in ' + self.tableName + '.')
             return True
        else:
            return False
    def CalculateField(self, FieldName, FieldValue):
        self.fieldName = FieldName
        self.fieldValue = FieldValue
        arcpy.AddMessage('In Table Class function CalculateField adding Line event fields FROM_MEAS, TO_MEAS and OFFSET to table ' + self.tableName + '.')
        arcpy.CalculateField_management(self.tableName, self.fieldName, self.fieldValue, "PYTHON", "")
        return
    def SelectFromQuery(self, Query, FieldList, SortField):
        # Example:  eventTable.SelectAndOrderRows('NAME','Viking Course',eventfieldList, 'MEAS')
        # Select an ordered set of Rows defined by the FieldName = FieldValue
        # The fields included are in the fieldList
        # The records are sorted by values in the SortField
        # Remove these
        # self.fieldName = FieldName    #  'NAME'                                             Name of field to filter on
        # self.fieldValue = FieldValue  #  'Viking Course'                                    Value of fields to filterself.query = "" + self.fieldName + " = '" + self.fieldValue + "'"  
        self.query = Query
        self.fieldList = FieldList    #  ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET']     List of fields to display
        self.sortField = SortField    #  'NAME'
        arcpy.AddMessage('In Table Class function SelectFromQuery ' + self.tableName + '.')
        try:                        
            # self.query = "" + self.fieldName + " = '" + self.fieldValue + "'"     
            arcpy.AddMessage('In Table Class function SelectFromQuery Query is ' + self.query + '.')
            arcpy.AddMessage('Showing values in self.sortField.')
            # Create the Search Cursor with the selected Rows            
            # with arcpy.da.SearchCursor(self.tableName, self.fieldList, self.query) as searchRows:
            self.selectedFields = []            
            with arcpy.da.SearchCursor(self.tableName, self.fieldList, self.query) as searchRows:            
                for searchRow in sorted(searchRows):  # for each row in the cursor
                    selectedValues = []
                    for fieldIndex in range(len(searchRow)):                        
                        selectedValues.append(searchRow[fieldIndex])
                        if (fieldIndex == 0):
                            rowMessage = str(searchRow[fieldIndex])                            
                        else:
                            rowMessage = rowMessage + '  ' + str(searchRow[fieldIndex])                            
                    arcpy.AddMessage(rowMessage)
                    self.selectedFields.append(selectedValues)
            del searchRows
        except Exception as e:
            errorMessage = 'Error in SelectAndOrderRows.  ' +  e.message
            arcpy.AddError(errorMessage)        
        return self.selectedFields
    def SelectAndOrderRows(self, FieldName, FieldValue, FieldList, SortField, SQLClause):
        # Example:  eventTable.SelectAndOrderRows('NAME','Viking Course',eventfieldList, 'MEAS')
        # Select an ordered set of Rows defined by the FieldName = FieldValue
        # The fields included are in the fieldList
        # The records are sorted by values in the SortField
        self.fieldName = FieldName    #  'NAME'                                             Name of field to filter on
        self.fieldValue = FieldValue  #  'Viking Course'                                    Value of fields to filter
        self.fieldList = FieldList    #  ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET']     List of fields to display        
        self.sqlClause = SQLClause    # (None,'ORDER BY MEAS')
        arcpy.AddMessage('In Table Class function SelectAndOrderRows ' + self.tableName + '.')
        try:            
            # self.query = '"' + self.fieldName + '" = ' + "'" + self.fieldValue + "'"
            self.query = "" + self.fieldName + " = '" + self.fieldValue + "'"     
            arcpy.AddMessage('In Table Class function SelectAndOrderRows Query is ' + self.query + '.')
            arcpy.AddMessage('Showing values in self.sortField for ' + self.query + '.')
            # Create the Search Cursor with the selected Rows            
            # with arcpy.da.SearchCursor(self.tableName, self.fieldList, self.query) as searchRows:
            self.selectedFields = []            
            with arcpy.da.SearchCursor(self.tableName, self.fieldList, self.query, sql_clause=self.sqlClause) as searchRows:                
                for searchRow in searchRows:  # for each row in the cursor
                    selectedValues = []
                    for fieldIndex in range(len(searchRow)):                        
                        selectedValues.append(searchRow[fieldIndex])
                        if (fieldIndex == 0):
                            rowMessage = str(searchRow[fieldIndex])                            
                        else:
                            rowMessage = rowMessage + '  ' + str(searchRow[fieldIndex])                            
                    arcpy.AddMessage(rowMessage)
                    self.selectedFields.append(selectedValues)
            del searchRows
            #if (len(selectedValues) == 0):
            #    noEventsOnRouteMessage = 'No events on route ' + self.query + '.'
            #    arcpy.AddMessage(noEventsOnRouteMessage)
        except Exception as e:
            errorMessage = 'Error in SelectAndOrderRows.  ' +  e.message
            arcpy.AddError(errorMessage)
        return self.selectedFields
    def GetAllFieldList(self):
        allFieldsList = []
        for field in arcpy.ListFields(self.tableName):
            allFieldsList.append(field.name)
        return allFieldsList
    def DeleteTable(self, tableName):
        # Delete the table if it exists.
        self.tableName = tableName
        if (arcpy.Exists(self.tableName)):
            arcpy.Delete_management(self.tableName)
            arcpy.AddMessage('Deleted table ' + self.tableName + '.')
        else:
            arcpy.AddMessage('Table ' + self.tableName + ' did not exist.')
        return        
class EventTable(Table):
    # Class to manage the Event Table
    def __init__(self, EventTableName, RouteFeatureClassName, RouteEventKeyField):
        # Initialize the Event Table
        self.eventTableName = EventTableName            # Name of the Table                                                 Example:    "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Groomed_Points\\Groomer_Locations"
        self.routeFeatureClassName = RouteFeatureClassName        # Name of the feature Class with the Routes                         Example:    "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Non_Motorized\\Ski_Routes"
        self.routeEventKeyField = RouteEventKeyField    # Name of the Field that will be key between Route and the Event:   EXample:    "NAME"
        return    
    def AddEventFields(self):
        # Add Field FROM_MEAS
        if (self.FieldExists('FROM_MEAS')):
            pass
        else:
            arcpy.AddMessage('In EventTable Class function AddEventFields adding Line event fields FROM_MEAS, TO_MEAS and OFFSET to ' + self.tableName + '.')
            arcpy.AddField_management(self.tableName, "FROM_MEAS", "LONG", "10", "", "", "From Measure", "NULLABLE", "NON_REQUIRED", "")

        # Add Field TO_MEAS
        if (self.FieldExists('TO_MEAS')):
            pass
        else:
            arcpy.AddMessage('In EventTable Class function AddEventFields.  Added Field TO_MEAS' + self.tableName + '.')
            arcpy.AddField_management(self.tableName, "TO_MEAS", "LONG", "10", "", "", "To Measure", "NULLABLE", "NON_REQUIRED", "")
        # Process: Add Field OFFSET
        if (self.FieldExists('OFFSET')):
            pass
        else:
            arcpy.AddField_management(self.tableName, "OFFSET", "LONG", "10", "", "", "Offset", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddMessage('In EventTable Class function AddEventFields.  Added Line event fields OFFSET to ' + self.tableName + '.')
        # Add filed DAYS_AGO
        if (self.FieldExists('DAYS_AGO')):
            pass
        else:
            arcpy.AddField_management(self.tableName, "DAYS_AGO", "LONG", "10", "", "", "Days since grooming", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddMessage('In EventTable Class function AddEventFields.  Added Line event fields DAYS_AGO to ' + self.tableName + '.')
        # Add filed HOURS_AGO
        if (self.FieldExists('HOURS_AGO')):
            pass
        else:
            arcpy.AddField_management(self.tableName, "HOURS_AGO", "LONG", "10", "", "", "Hours since grooming", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddMessage('In EventTable Class function AddEventFields.  Added Line event fields HOURS_AGO to ' + self.tableName + '.')
        return
    def CalculateFieldTO_MEAS(self):
        # Calculate Field TO_MEAS to the MEAS value which is the groomer point.
        arcpy.CalculateField_management(self.tableName, "TO_MEAS", "int(!MEAS!)", "PYTHON", "")
        return
    def CalculateFieldOFFSET(self):
        # Calculate Field OFFSET to 0
        arcpy.CalculateField_management(self.tableName, "OFFSET", 0, "PYTHON", "")
        return
    def CalculateFieldFROM_MEAS(self, FieldName, FieldValue, FieldList, SortField, FromField, SQLClause):
        # Example  CalculateFieldFROM_MEAS('NAME','Viking Course',  ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET'], 'MEAS' 'FROM_MEAS'):
        # Calculate Field FROM_MEASURE which will be 0 for the first record on the route, and the previous TO_MEAS for other records.
        # Select an ordered set of Rows defined by the FieldName = FieldValue
        # The fields included are in the fieldList
        # The records are sorted by values in the SortField
        self.fieldName = FieldName    #  'NAME'                                          Name of the field to filter for.  In this case NAME             
        self.fieldValue = FieldValue  #  'Viking Course'                                 Value of the records to filter on.  In this case a trail  
        self.fieldList = FieldList    #  ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET']  List of fields in the cursor                               
        self.sortField = SortField    #  'MEAS'                                          Field the records are sorted on.
        self.fromField = FromField    #  'FROM_MEAS'                                     Field that will be calculated as 0 or preivous value for trail.
        self.sqlClause = SQLClause    #  (None,'ORDER BY MEAS')                          Pre SQL Clause and Post SQL Clause (None,None)         
        # An optional pair of SQL prefix and postfix clauses organized in a list or tuple.
        # SQL prefix supports None, DISTINCT, and TOP. SQL postfix supports None, ORDER BY, and GROUP BY.
        # An SQL prefix clause is positioned in the first position and will be inserted between the SELECT keyword and the SELECT COLUMN LIST. The SQL prefix clause is most commonly used for clauses such as DISTINCT or ALL.
        # An SQL postfix clause is positioned in the second position and will be appended to the SELECT statement, following the where clause. The SQL postfix clause is most commonly used for clauses such as ORDER BY.        
        # DISTINCT, ORDER BY, and ALL are only supported when working with databases. They are not supported by other data sources (such as dBASE or INFO tables).
        # TOP is only supported by SQL Server and MS Access databases.  
        # http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/searchcursor-class.htm#C_GUID-3CB1DFF4-983D-445F-9CB2-0FF1CD4B4880
        #
        if self.fieldValue == None:
            self.fieldValue = "Unamed"
            arcpy.AddMessage('In EventTable Class function CalculateFieldFROM_MEAS ' + ' ' + self.fieldName + ' = ' + self.fieldValue + " Name was None.  You should fix this before running again.")
        else:
            arcpy.AddMessage('In EventTable Class function CalculateFieldFROM_MEAS ' + ' ' + self.fieldName + ' = ' + self.fieldValue)
        try:            
            # self.query = '"' + self.fieldName + '" = ' + "'" + self.fieldValue + "'"
            self.query = "" + self.fieldName + " = '" + self.fieldValue + "'"            
            arcpy.AddMessage('In EventTable Class function CalculateFieldFROM_MEAS.')
            arcpy.AddMessage('Showing values in ' + self.sortField)
            # Get the Index of the Sort and Measure Field
            self.measureFieldIndex = self.fieldList.index(self.sortField)
            # Get the index of the From Field
            self.fromFieldIndex = self.fieldList.index(self.fromField)
            # Create the Update Cursor with the selected Rows
            # with arcpy.da.UpdateCursor(self.tableName, self.fieldList, self.query) as searchRows:
            fromMeasure = 0  # First Row in trail is 0
            with arcpy.da.UpdateCursor(self.tableName, self.fieldList, self.query, sql_clause=self.sqlClause) as updateCursor:
                for row in updateCursor:  # for each row in the cursor
                    row[self.fromFieldIndex] = fromMeasure
                    updateCursor.updateRow(row)
                    fromMeasure = int(row[self.measureFieldIndex])
                    # Display the values of the row                    
                    for fieldIndex in range(len(row)):
                        if (fieldIndex == 0):
                            rowMessage = str(row[0])
                        else:
                            rowMessage = rowMessage + '  ' + str(row[fieldIndex])
                    arcpy.AddMessage(rowMessage)
                                
        except Exception as e:
            errorMessage = 'Error in CalculateFieldFROM_MEAS' + e.message            
            arcpy.AddError(errorMessage)
                   
        return
    def AddRecordsAfterGroomerPoint(self, FieldName, FieldValue, FieldList, SortField, FromField, SQLClause, TrailLength):
        # Example  AddRecordsAfterGroomerPoint('NAME','Viking Course',  ['NAME','MEAS','FROM_MEAS','TO_MEAS','OFFSET'], 'MEAS' 'FROM_MEAS'):
        # Calculate Field FROM_MEASURE which will be 0 for the first record on the route, and the previous TO_MEAS for other records.
        # Select an ordered set of Rows defined by the FieldName = FieldValue
        # The fields included are in the fieldList
        # The records are sorted by values in the SortField        
        self.fieldName = FieldName    #  'NAME'                                          Name of the field to filter for.  In this case NAME             
        self.fieldValue = FieldValue  #  'Viking Course'                                 Value of the records to filter on.  In this case a trail  
        self.fieldList = FieldList    #  [all fields in event table]                List of fields in the cursor
        self.sortField = SortField    #  'MEAS'                                          Field the records are sorted on.
        self.fromField = FromField    #  'FROM_MEAS'                                     Field that will be calculated as 0 or preivous value for trail.
        self.sqlClause = SQLClause    #  (None,'ORDER BY MEAS')                          Pre SQL Clause and Post SQL Clause (None,None)         
        self.trailLength = TrailLength  # Length of trail from the trail length table.
        self.allFieldsList = arcpy.ListFields(self.eventTableName)  # All fields in table 
        # An optional pair of SQL prefix and postfix clauses organized in a list or tuple.
        # SQL prefix supports None, DISTINCT, and TOP. SQL postfix supports None, ORDER BY, and GROUP BY.
        # An SQL prefix clause is positioned in the first position and will be inserted between the SELECT keyword and the SELECT COLUMN LIST. The SQL prefix clause is most commonly used for clauses such as DISTINCT or ALL.
        # An SQL postfix clause is positioned in the second position and will be appended to the SELECT statement, following the where clause. The SQL postfix clause is most commonly used for clauses such as ORDER BY.        
        # DISTINCT, ORDER BY, and ALL are only supported when working with databases. They are not supported by other data sources (such as dBASE or INFO tables).
        # TOP is only supported by SQL Server and MS Access databases.  
        # http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/searchcursor-class.htm#C_GUID-3CB1DFF4-983D-445F-9CB2-0FF1CD4B4880
        ###
        if self.fieldValue == None:
            self.fieldValue  = "Unnamed"
            arcpy.AddMessage('Blank Trail name is now ' + self.fieldValue)        
        arcpy.AddMessage('In EventTable Class function AddRecordsAfterGroomerPoint ' + ' ' + self.fieldName + ' = ' + self.fieldValue)
        try:            
            # self.query = '"' + self.fieldName + '" = ' + "'" + self.fieldValue + "'"
            self.query = "" + self.fieldName + " = '" + self.fieldValue + "'"            
            arcpy.AddMessage('In EventTable Class function CalculateFieldFROM_MEAS.')
            arcpy.AddMessage('Showing values in ' + self.sortField)
            # Get the Index of the Sort and Measure Field
            self.measureFieldIndex = self.fieldList.index(self.sortField)
            # Get the index of the From Field
            self.fromFieldIndex = self.fieldList.index(self.fromField)
            # Create the Update Cursor with the selected Rows
            # with arcpy.da.UpdateCursor(self.tableName, self.fieldList, self.query) as searchRows:            
            selectedValues = []  # Was here.  Can be deleted if it works in the new spot.
            with arcpy.da.SearchCursor(self.tableName, self.fieldList, self.query, sql_clause=self.sqlClause) as searchCursor:                                       
                for searchRow in searchCursor:  # for each row in the searchCursor
                    # Display the values of the row
                    selectedValues = []
                    for fieldIndex in range(len(searchRow)):
                        selectedValues.append(searchRow[fieldIndex])
                    eventTagName = self.allFieldsList[12].name
                    fromMeasureName = self.allFieldsList[19].name
                    selectedValues[12] = 'Added to End'
                    selectedValues[19] = selectedValues[20]    # To Measure will equal the frem measure
                    selectedValues[20] = int(self.trailLength)
                    arcpy.AddMessage('In EventTable Class function AddRecordsAfterGroomerPoint FROM_MEAS is '+ fromMeasureName + ' is ' + str(selectedValues[20]))
                    arcpy.AddMessage('In EventTable Class function AddRecordsAfterGroomerPoint EVENTTAG  is '+ eventTagName + ' is ' + selectedValues[12])
            if (len(selectedValues) > 24):
                selectedValues = []
            else:
                if (len(selectedValues) > 0):
                    with arcpy.da.InsertCursor(self.tableName, self.fieldList) as insertCursor:
                        insertCursor.insertRow(selectedValues)
        except Exception as e:
            errorMessage = 'EventTable Class function AddRecordsAfterGroomerPoint' + e.message            
            arcpy.AddError(errorMessage)           
        return
    def AddEventLayer(self,RouteFeatureClassName,EventTableName, EventsLayerFileName):
        # Purpose:  Add an Event Layer to the Map
        # Parameters:  RouteFeatureClassName = name of the route feature class
        #              EventTableName        = name of the Event table take contains measures
        #              EventsLayerFileNmae   = name of the layer file that will be used for symbolization        
        self.routeFeatureClassName = RouteFeatureClassName
        self.eventTableName = EventTableName
        self.eventTableProperties = 'NAME LINE FROM_MEAS TO_MEAS'
        self.eventLayerName = 'GroomerEvents'
        self.routeIDField = 'NAME'
        # self.offsetField = 'OFFSET'
        self.errorField = 'ERROR_FIELD'        
        arcpy.AddMessage('In EventTable Class  AddEventLayer')
        # arcpy.MakeRouteEventLayer_lr(Ski_Routes, "NAME", CabinCreekGroomerEvents_Test, "NAME LINE FROM_MEAS TO_MEAS", CabinCreekGroomerEvents_Events, "OFFSET", "ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        # Make the EventLayer in memory for display
        try:            
            arcpy.MakeRouteEventLayer_lr(self.routeFeatureClassName, self.routeIDField, self.eventTableName, self.eventTableProperties, self.eventLayerName, "OFFSET", "ERROR_FIELD")
            arcpy.AddMessage('Made Route Event Layer ' + self.eventLayerName)
            self.eventsLayerFileName = EventsLayerFileName # 'Ski Grooming Events by Day'            
            # CabinCreekGroomerEvents_Events = "CabinCreekGroomerEvents Events"
            # GroomerEvents_lyr = "C:\\AtlasTrackExample\\Trails\\Layers\\GroomerEvents.lyr"
            # arcpy.ApplySymbologyFromLayer_management(CabinCreekGroomerEvents_Events, GroomerEvents_lyr)
            arcpy.ApplySymbologyFromLayer_management(self.eventLayerName, self.eventsLayerFileName)            # Line 446 should not be commented out
            arcpy.AddMessage('Applied symbology from  ' + self.eventsLayerFileName)            
        except Exception as e:
            errorMessage = 'Error in AddEventLayer  ' + e.message
            arcpy.AddError(errorMessage)            
        return
    def CalculateFieldDAYS_AGO(self):
        # Calculate Field DAYS_AGO to the number of days from now
        arcpy.CalculateField_management(self.tableName, "DAYS_AGO", "(datetime.date.today() - datetime.date(int(!LOCAL_DATE!.split('/')[2]), int(!LOCAL_DATE!.split('/')[0]), int(!LOCAL_DATE!.split('/')[1]))).days", "PYTHON", "")
        return    
    def CalculateFieldHOURS_AGO(self):
        # Calculate Field HOURS_AGO to number of hours from now to grooming completion
        arcpy.CalculateField_management(self.tableName,  "HOURS_AGO", "(!DAYS_AGO! * 24) + int(!LOCAL_TIME!.split(':')[0])", "PYTHON", "")
        return
    def LocateFeaturesAlongRoutes(self, PointFeatureClass, SearchDistance):
        # Purpose: Create a Point Event Layer from a Point layer by locating the points along the routes
        # Parameters:   PointFeatureClass   = The Feature Class with the Points that will be mapped along the route     Example:   "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Groomed_Points\\Groomer_Locations"
        #               SearchDistance      = Distance from the line to search for                                      Example:   "100 Feet"
        # Process: Locate Features Along Routes from Model                                        
        self.pointFeatureClass = PointFeatureClass
        self.searchDistance = SearchDistance
        
        outputEventTableProperties = "NAME POINT MEAS"  
        # arcpy.LocateFeaturesAlongRoutes_lr(in_features,          in_routes,                  route_id_field,    SearchDistance,      out_table,     out_event_properties,             route_locations,distance_field,zero_length_events,in_fields,m_direction_offsetting)
        # arcpy.LocateFeaturesAlongRoutes_lr(Groomer_Locations,    Ski_Routes,                 "NAME",            "100 Feet",          GroomerEvents, Output_Event_Table_Properties,    "FIRST",        "DISTANCE",    "ZERO",           "FIELDS",  "M_DIRECTON")
        try:
            if (arcpy.Exists(self.eventTableName)):  # Delete the table if it exists already.
                self.DeleteTable(self.eventTableName)
            arcpy.LocateFeaturesAlongRoutes_lr(self.pointFeatureClass, self.routeFeatureClassName, self.routeEventKeyField, self.searchDistance, self.eventTableName, outputEventTableProperties, "FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")
            arcpy.AddMessage('Created event table ' + self.eventTableName + ' by locating points from ' + self.pointFeatureClass + ' along the routes ' + self.routeFeatureClassName + ' with ' + self.routeEventKeyField + ' and search distance of ' + self.searchDistance + '.')
            return True
        except Exception as e:
            arcpy.AddMessage('Error:  Did not create event table ' + self.eventTableName + ' by locating points from ' + self.pointFeatureClass + ' along the routes ' + self.routeFeatureClassName + ' with ' +  self.routeEventKeyField + ' and search distance of ' + self.searchDistance + '.')            
            errorMessage = 'Error in EventTable Locate FeaturesAlongRoutes is ' + e.message
            arcpy.AddError(errorMessage) 
            return False        
    def MakeRouteEventLayer(self, EventLayerName):
        # Process: Make Route Event Layer
        self.eventLayerName = EventLayerName
        arcpy.MakeRouteEventLayer_lr(self.routeFeatureClassName, "NAME", self.eventTableName, "NAME POINT meas", self.eventLayerName, "", "ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        return
class Route(Table):
    def __init__(self, RouteFeatureClassName):
        self.routeFeatureClassName = RouteFeatureClassName  # routeTableName = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Ski_Routes'
        if arcpy.Exists(self.routeFeatureClassName):
            self.routeFeatureClassName = self.routeFeatureClassName
            self.tableName = self.routeFeatureClassName
            arcpy.AddMessage('In Route Class __init__ ' + self.routeFeatureClassName + ' exists.')
            arcpy.RefreshCatalog(self.routeFeatureClassName)  # Refreshed the Table so that it see the latest structure.
        else:
            arcpy.AddMessage('In Route Class __init__ ' + self.routeFeatureClassName + ' does not exist.')
        return
    def GetRouteLength(self):
        # Get a length of a trail from the route table.
        routeTableName = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Ski_Routes'
        shapeFieldsList = ['NAME','Shape_Length']
        routeTable = Table(routeTableName)
        sqlClause = (None,'ORDER BY MEAS')
        routeTableQuery = routeTable.SelectAndOrderRows("NAME",'Viking Course', shapeFieldsList, 'Shape_Length', sqlClause)
        routeLength = routeTableQuery[0][1]
        routeName = routeTableQuery[0][0]
        arcpy.AddMessage(routeName + ' is ' + str(routeLength) + ' feet long.')
        return
class ListClass():
    def __init__(self, ListIn):
        self.listIn = ListIn
    def DisplayColum1(self):
        pass
    def DisplayList(self):
        arcpy.AddMessage('Display of List')
        cols = len(self.listIn)
        rows = 0
        if cols:
            rows = len(self.listIn[0])
        for j in range(rows):
            for i in range(cols):
                arcpy.AddMessage(str(self.listIn[i][j]))
        return
    def DisplayTrails(self):
        trailsList = []
        arcpy.AddMessage('Display Trails')
        cols = len(self.listIn)        
        if cols:
            # rows = len(self.listIn[0])
            for i in range(cols):            
                arcpy.AddMessage(str(self.listIn[i][0]))
                trailsList.append(self.listIn[i][0])
        return trailsList
    def DisplayTrailLengths(self):
        trailsLengthList = []
        arcpy.AddMessage('Display Trail Lengths')
        cols = len(self.listIn)        
        if cols:
            # rows = len(self.listIn[0])
            for i in range(cols):            
                arcpy.AddMessage(str(self.listIn[i][1]))
                trailsLengthList.append(self.listIn[i][1])
        return trailsLengthList
class LayerFile():
    def __init__(self, LayerFileName):
        self.layerFileName = LayerFileName    
        if arcpy.Exists(self.layerFileName):
            arcpy.AddMessage('In LayerFile Class __init__ ' + self.layerFileName + ' exists.')
            # arcpy.RefreshCatalog(self.tableName)  # Refreshed the Table so that it see the latest structure.
            self.layerFileNameExists = True
        else:
            arcpy.AddError('In LayerFile  Class __init__ ' + self.layerFileName + ' does not exist.')
            self.layerFileNameExists = False
        return
class CSVFile():
    def __init__(self, CSVFileName):
        self.csvFileName = CSVFileName    
        if arcpy.Exists(self.csvFileName):
            arcpy.AddMessage('In CSVFile Class __init__ ' + self.csvFileName + ' exists.')            
            self.csvFileNameExists = True
        else:
            arcpy.AddError('In CSVFile  Class __init__ ' + self.csvFileName + ' does not exist.')
            self.csvFileNameExists = False
        return
    def MakeXYEventLayer(self, GroomerLocations):
        # self.groomerLocationsMultipart = "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Groomed_Points\\Groomer_LocationsMultipart"
        self.groomerLocations = GroomerLocations  # "C:\\AtlasTrackExample\\Trails\\WinterTrailsStatePlane.gdb\\Groomed_Points\\Groomer_Locations"
        self.groomerLocationsXY = "GroomerLocationsXY"
        try:
            # Process: Make XY Event Layer
            arcpy.MakeXYEventLayer_management(self.csvFileName, "longitude", "latitude", self.groomerLocationsXY, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "")
            # Process: Project.  This is already projected by placing it in the feature dataset
            # arcpy.Project_management(self.groomerLocationsXY, self.groomerLocationsMultipart, "PROJCS['NAD83_HARN_Washington_South_ftUS',GEOGCS['GCS_NAD83(HARN)',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['false_easting',1640416.667],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-120.5],PARAMETER['standard_parallel_1',45.83333333333334],PARAMETER['standard_parallel_2',47.33333333333334],PARAMETER['latitude_of_origin',45.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
            # Process: Multipart To Singlepart
            if (arcpy.Exists(self.groomerLocations)):
                arcpy.Delete_management(self.groomerLocations,None)
            arcpy.MultipartToSinglepart_management(self.groomerLocationsXY, self.groomerLocations)
            # Process: Delete Identical.   Added to remove any duplicates.
            arcpy.DeleteIdentical_management(self.groomerLocations, "Shape;UNIQUEID;COLLECTIONDATE;COLLECTIONTIME;LATITUDE;LONGITUDE;BEARING;SPEED;EVENTCODE;EVENTTAG;ESN;ALT_ESN;UNITID;LOCAL_DATE;LOCAL_TIME;ORIG_FID", "", "0")
        except Exception as e:
            errorMessage = 'Error in CSVFile Class Method AddEventLayer  ' + e.message
            arcpy.AddError(errorMessage)
        return
class MapDocument():
    def __init__(self, MapDocumentFile):
        self.mapDocumentFile = MapDocumentFile
        if arcpy.Exists(self.mapDocumentFile):
            arcpy.AddMessage('In MapDocument Class __init__ ' + self.mapDocumentFile + ' exists.')
            self.mapDocument = arcpy.mapping.MapDocument(self.mapDocumentFile)
            self.mapDocumentExists = True
        else:
            arcpy.AddError('In MapDocument Class __init__ ' + self.mapDocumentFile + ' does not exist.')
            self.mapDocumentExists = False
        return
    def AddLayerToMap(self, LayerFile):
        # mxd = arcpy.mapping.MapDocument("CURRENT")
        # mxd = arcpy.mapping.MapDocument(r'C:\AtlasTrackExample\Trails\ArcMap\WinterTrails.mxd')        
        self.layerFile = LayerFile  # Should be r'C:\AtlasTrackExample\Trails\Layers\GroomerEvents.lyr'
        if arcpy.Exists(self.mapDocumentFile):
            arcpy.AddMessage('In MapDocument Class AddLayerToMap ' + self.layerFile + ' exists.')            
            self.mapDocument = arcpy.mapping.MapDocument(self.mapDocumentFile)
            dataframe = arcpy.mapping.ListDataFrames(self.mapDocument)[0]
            eventLayer = arcpy.mapping.Layer(self.layerFile)
            arcpy.mapping.AddLayer(dataframe, eventLayer, "BOTTOM")
            arcpy.RefreshTOC
            arcpy.RefreshActiveView
            self.layerFileExists = True
        else:            
            arcpy.AddMessage('In MapDocument Class AddLayerToMap ' + self.layerFile + ' does not exist.')            
            self.layerFileExists = False            
        return
    def SaveMapDocumentCopy(self):
        # This should be changed to save the existing Document
        self.mapDocumentCopyFile = r'C:\AtlasTrackExample\Trails\ArcMap\WinterTrails_New.mxd'
        self.mapDocument.saveACopy(self.mapDocumentCopyFile)
        arcpy.AddMessage('Class MapDocument Saved a copy of the map to ' + self.mapDocumentCopyFile)
        return        
    def SaveMapDocument(self):
        # This should be changed to save the existing Document
        self.mapDocument.save()
        arcpy.AddMessage('Class MapDocument Saved the map ' + self.mapDocumentFile)
        return        
def main(params):
    arcpy.AddMessage('------------------------------------------------------------------------------------------------------------------')
    arcpy.AddMessage('In Program main. Checking Parameters')
    arcpy.AddMessage('In EventTableTool Execute 0 Response.csv               Parameter is ' + param0)
    arcpy.AddMessage('In EventTableTool Execute 1 GroomerLocations           Parameter is ' + param1)
    arcpy.AddMessage('In EventTableTool Execute 2 AreaOfInterest             Parameter is ' + param2)
    arcpy.AddMessage('In EventTableTool Execute 3 AreaOfInterestExpression   Parameter is ' + param3)
    arcpy.AddMessage('In EventTableTool Execute 4 Table input                Parameter is ' + param4)
    arcpy.AddMessage('In EventTableTool Execute 5 Route Feature Class        Parameter is ' + param5)
    arcpy.AddMessage('In EventTableTool Execute 6 Event Layer File Name      Parameter is ' + param6)
    arcpy.AddMessage('------------------------------------------------------------------------------------------------------------------')
    #  Main function for debugging
    # toolbox = Toolbox()
    # eventTableName = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\CabinCreekGroomerEvents_Test'
    eventTableTool = EventTableTool()
    messages = "Running Table Tool"     
    # param0.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\CabinCreekGroomerEvents_Test'    
    # param1.value = r'C:\AtlasTrackExample\Trails\WinterTrailsStatePlane.gdb\Ski_Routes'
    ## eventTableTool.execute(eventTableTool.getParameterInfo(), messages)
    eventTableTool.execute(params, messages)
    return
if __name__ == '__main__':
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)
    param2 = arcpy.GetParameterAsText(2)
    param3 = arcpy.GetParameterAsText(3)
    param4 = arcpy.GetParameterAsText(4)
    param5 = arcpy.GetParameterAsText(5)
    param6 = arcpy.GetParameterAsText(6)    
    params =[param0, param1, param2, param3, param4, param5, param6]
    main(params)