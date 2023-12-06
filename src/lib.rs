// Import external libraries
extern crate num;
extern crate evalexpr;
extern crate gethostname;
extern crate dicom;
// extern crate rayon;

// Import internal libraries
use pyo3::prelude::*;
use rayon::prelude::*;
use num::integer::div_ceil;
use evalexpr::{eval_int, eval_number};
use gethostname::gethostname;
use dicom::core::*;
use dicom::object::open_file;
// use rayon::prelude::*;

// Constants
static DEFAULT_IMG_TYPE: &str = "UNK";


// Function to anonymize a DICOM file
fn anonymize_file(
    path: String,
    new_path: String,
    name_convention: bool
) -> bool {
    // Open DICOM file
    let mut file = open_file(path).unwrap();

    // Retrieve ImageType DICOM tag
    let img_type_tag = match file.element(Tag(0x0008, 0x0008)) {
        Ok(tag) => tag.to_str().unwrap().to_string(),
        Err(_) => "".to_string(),
    };

    let img_type_list: Vec<&str> = img_type_tag.split('/').collect();
    let img_type = if img_type_list.len() > 2 {
        img_type_list[2].to_string()
    } else {
        DEFAULT_IMG_TYPE.to_string()
    };

    // Retrieve DeviceSerialNumber DICOM tag
    let serial_num = match file.element(Tag(0x0018, 0x1000)) {
        Ok(tag) => tag.to_str().unwrap().to_string(),
        Err(_) => "".to_string(), // datetime.today().strftime("%Y%m%d")
    };

    if !serial_num.chars().all(char::is_numeric) {
        println!("DeviceSerialNumber <{}> is not numeric.", serial_num);
        return false;
    }

    // Retrieve DICOM tags
    let tags = [
        Tag(0x0018, 0x1000),    // DeviceSerialNumber
        Tag(0x0008, 0x0020),    // StudyDate
        Tag(0x0008, 0x0030),    // StudyTime
        Tag(0x0020, 0x000D),    // StudyInstanceUID
        Tag(0x0010, 0x0030),    // PatientBirthDate
    ];

    let values: Vec<_> = tags.par_iter()
        .map(|tag|
            match file.element(*tag) {
                Ok(tag_value) => tag_value.to_str().unwrap().to_string(),
                Err(_) => "".to_string(),
            })
        .collect();

    // Create new values
    let new_pid = format!("{}{}{}",
        serial_num,
        &values[1][2..8],
        &values[2][0..4]);
    let new_study_date = format!("{}0101", &values[1][0..4]);
    let new_birth_date = format!("{}0101", &values[4][0..4]);
    let new_station = gethostname().into_string().unwrap();

    // Reformat new_pid
    let new_pid = i64::from_str_radix(&new_pid, 10)
        .map(|n| format!("{:X}", n))
        .unwrap();

    // Reformat study_uid
    let study_uid = eval_int(values[3].replace(".", "+").as_str()).map(|n| format!("{:X}", n)).unwrap();

    // Create a vector of (tag, VR, value) tuples for each changed DICOM tags
    let tags = vec![
        (Tag(0x0008, 0x1010), VR::SH, &new_station),
        (Tag(0x0008, 0x0012), VR::DA, &new_study_date),
        (Tag(0x0008, 0x0020), VR::DA, &new_study_date),
        (Tag(0x0008, 0x0021), VR::DA, &new_study_date),
        (Tag(0x0008, 0x0022), VR::DA, &new_study_date),
        (Tag(0x0008, 0x0023), VR::DA, &new_study_date),
        (Tag(0x0008, 0x0050), VR::SH, &study_uid),
        (Tag(0x0010, 0x0010), VR::PN, &new_pid),
        (Tag(0x0010, 0x0020), VR::LO, &new_pid),
        (Tag(0x0010, 0x0030), VR::DA, &new_birth_date),
        (Tag(0x0020, 0x0010), VR::DA, &study_uid),
    ];

    // Change DICOM tags according to new values
    for (tag, vr, value) in tags.into_iter() {
        let primitive_value = dicom::core::PrimitiveValue::from(value.to_string());
        let dicom_value = DicomValue::from(primitive_value);
        let data_element = DataElement::new(tag, vr, dicom_value);
        file.put_element(data_element);
    }

    // Clear specific DICOM tags
    let tags_to_remove = vec![
        Tag(0x0008, 0x0080),    // InstitutionName
        Tag(0x0008, 0x0081),    // InstitutionAddress
        Tag(0x0008, 0x0090),    // ReferringPhysicianName
        Tag(0x0008, 0x0092),    // ReferringPhysicianAddress
        Tag(0x0008, 0x0094),    // ReferringPhysicianTelephoneNumbers
        Tag(0x0008, 0x1040),    // InstitutionalDepartmentName
        Tag(0x0008, 0x1048),    // PhysiciansOfRecord
        Tag(0x0008, 0x1049),    // PhysiciansOfRecordIdentificationSequence
        Tag(0x0008, 0x1050),    // PerformingPhysicianName
        Tag(0x0008, 0x1060),    // NameOfPhysiciansReadingStudy
        Tag(0x0008, 0x1070),    // OperatorsName
        Tag(0x0008, 0x1080),    // AdmittingDiagnosesDescription
        Tag(0x0010, 0x1000),    // OtherPatientIDs
        Tag(0x0010, 0x1001),    // OtherPatientNames
        Tag(0x0010, 0x1090),    // MedicalRecordLocator
        Tag(0x0010, 0x2160),    // EthnicGroup
        Tag(0x0010, 0x2180),    // Occupation
        Tag(0x0010, 0x21B0),    // AdditionalPatientHistory
        Tag(0x0010, 0x4000),    // PatientComments
        Tag(0x0032, 0x1032),    // RequestingPhysician
        Tag(0x0032, 0x1033),    // RequestingService
        Tag(0x0032, 0x1060),    // RequestedProcedureDescription
        Tag(0x0040, 0x0006),    // ScheduledPerformingPhysicianName
        Tag(0x0040, 0x0241),    // PerformedStationAETitle
        Tag(0x0040, 0x0275),    // RequestAttributesSequence
        Tag(0x0040, 0x1001),    // RequestedProcedureID
        Tag(0x0040, 0x2004),    // IssueDateOfImagingServiceRequest
        Tag(0x0040, 0xA730),    // ContentSequence
    ];

    for tag in tags_to_remove {
        file.remove_element(tag);
    }

    // Control if parent directory exists
    let mut file_path = std::path::PathBuf::from(new_path);
    if let Some(file_dir) = file_path.parent() {
        std::fs::create_dir_all(file_dir).unwrap();
    }

    // Create new file path according to file name convention if needed
    if name_convention {
        // Extract DICOM tags
        let series_uid = match file.element(Tag(0x0020, 0x000E)) {
            Ok(tag) => tag.to_str().unwrap().to_string(),
            Err(_) => "".to_string(),
        };

        let modality = match file.element(Tag(0x0008, 0x0060)) {
            Ok(tag) => tag.to_str().unwrap().to_string(),
            Err(_) => "".to_string(),
        };

        let mut inst_num = match file.element(Tag(0x0020, 0x0013)) {
            Ok(tag) => tag.to_str().unwrap().to_string(),
            Err(_) => "".to_string(),
        };
        inst_num = format!("{:05}", inst_num.parse::<u32>().unwrap());

        // Reformat series_uid
        let series_uid = series_uid.replace(".", "+");
        let mut series_uid = match eval_number(series_uid.as_str()) {
            Ok(val) => val,
            Err(_) => 1234567891234567.
        };
        while series_uid / 10. == div_ceil(series_uid as i128, 10) as f64 {
            series_uid /= 10.;
        }
        let series_uid = format!("{:X}", series_uid as i128);

        // Create new directories
        file_path = file_path.join(&new_pid)
            .join(&study_uid)
            .join(&series_uid.to_string());
        if let Err(_) = std::fs::create_dir_all(&file_path) {
            eprintln!("Error creating directory {}.", file_path.display());
            return false;
        }

        // Create new DICOM file name
        file_path = file_path
            .join(format!("{}_{}_{}.dcm", modality, img_type, inst_num));
    }

    // Save anonymized file
    let result = file.write_to_file(file_path);
    if result.is_err() {
        println!("{}", result.unwrap_err().to_string());
    }

    return true;
}

/// Anonymize all files within a directory.
#[pyfunction]
fn anonymize_dicomdir(path: Vec<String>, new_path: String) -> PyResult<bool> {
    // Loop over all files
    let nb_anonymized_files = path
        .par_iter()
        .filter_map(|file| {
            if anonymize_file(file.clone().clone(), new_path.clone(), true) {
                Some(())
            } else {
                None
            }
        })
        .count();

    // Print number of anonymized files
    println!("{} files anonymized.", nb_anonymized_files);
    return Ok(true);
}


/// Format the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(anonymize_dicomdir, m)?)?;
    Ok(())
}
