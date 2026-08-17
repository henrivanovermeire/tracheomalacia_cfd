import slicer
from DICOMLib import DICOMUtils

source_folder = "/home/hvoverme/tracheomalacia_cfd/segmentation/source/ct-lung-screening-nlst-series" # change to source folder location

# Load DICOM files into the current scene

with DICOMUtils.TemporaryDICOMDatabase() as db:
    
    DICOMUtils.importDicom(source_folder, db)
    
    patientUID = db.patients()[0]
    DICOMUtils.loadPatientByUID(patientUID)
# Create segmentation node

segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")

segmentation = segmentation_node.GetSegmentation()

for segment in ["Airways", "Lungs", "Ither"]:
    segmentation.AddEmptySegment(segment)
