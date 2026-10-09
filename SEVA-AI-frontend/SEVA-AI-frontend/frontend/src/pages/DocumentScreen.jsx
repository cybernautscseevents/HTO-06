import { useState } from "react";
import { uploadDocument } from "../services/api";

function formatCurrency(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return `₹${number.toLocaleString("en-IN")}`;
}

function getMismatchMessage(mismatch) {
  switch (mismatch.field) {
    case "document_type":
      return `Wrong document uploaded. Expected ${mismatch.provided}, but the uploaded file appears to be ${mismatch.document}.`;

    case "name":
      return `Name mismatch. Your profile says "${mismatch.provided}", but the document says "${mismatch.document}".`;

    case "income":
      return `Income mismatch. Your profile says ${formatCurrency(
        mismatch.provided
      )}, but the document says ${formatCurrency(
        mismatch.document
      )}.`;

    default:
      return `${mismatch.field}: ${mismatch.provided} vs ${mismatch.document}`;
  }
}

function getRequirementLabel(action) {
  if (action === "upload") {
    return "Document upload required";
  }

  if (action === "provide_information") {
    return "Information required";
  }

  if (action === "conditional") {
    return "Conditional requirement";
  }

  return "Requirement";
}

function getVerificationTitle(verification) {
  if (!verification) {
    return "Verification pending";
  }

  if (verification.verified) {
    return "Document verified successfully";
  }

  const hasDocumentTypeMismatch =
    verification.mismatches?.some(
      (item) => item.field === "document_type"
    );

  if (hasDocumentTypeMismatch) {
    return "Wrong document uploaded";
  }

  return "Document verification failed";
}

export default function DocumentScreen({
  selectedScheme,
  profile,
  onBack,
  onComplete,
}) {
  const [uploadingIndex, setUploadingIndex] = useState(null);
  const [results, setResults] = useState({});
  const [errors, setErrors] = useState({});
  const [providedInformation, setProvidedInformation] =
    useState({});

  const requirements =
    selectedScheme?.document_requirements || [];

  const handleFileUpload = async (
    file,
    requirement,
    index
  ) => {
    if (!file) {
      return;
    }

    setUploadingIndex(index);

    setErrors((previous) => ({
      ...previous,
      [index]: null,
    }));

    try {
      const response = await uploadDocument(
        file,
        requirement.name,
        profile?.name || "",
        profile?.income ?? ""
      );
      console.log("Document upload response:", response);
console.log("Extracted data:", response?.extracted_data);

      setResults((previous) => ({
        ...previous,
        [index]: response,
      }));
    } catch (error) {
      console.error(
        "Document upload failed:",
        error
      );

      setErrors((previous) => ({
        ...previous,
        [index]:
          error.message ||
          "Failed to upload document.",
      }));
    } finally {
      setUploadingIndex(null);
    }
  };

  const handleContinue = () => {
    const information = {};

    requirements.forEach((requirement, index) => {
      if (
        requirement.action ===
        "provide_information"
      ) {
        information[requirement.name] =
          providedInformation[index] || "";
      }
    });

    if (onComplete) {
      onComplete({
        providedInformation: information,
        verificationResults: results,
      });
    }
  };

  if (!selectedScheme) {
    return (
      <div className="page-shell">
        <div className="empty-state-card">
          <h2>No scheme selected</h2>

          <p>
            Please select a government scheme
            before continuing.
          </p>

          {onBack && (
            <button
              className="primary-button"
              onClick={onBack}
            >
              Back to schemes
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell document-page">
      <div className="document-header">
        <div>
          <p className="eyebrow">DOCUMENTS</p>

          <h1>Prepare your application</h1>

          <p className="page-description">
            Upload or provide only the requirements
            for the scheme you selected.
          </p>
        </div>

        {onBack && (
          <button
            className="secondary-button"
            onClick={onBack}
          >
            ← Back to schemes
          </button>
        )}
      </div>

      <div className="selected-scheme-banner">
        <div>
          <span className="banner-label">
            Selected scheme
          </span>

          <h2>
            {selectedScheme.scheme_name}
          </h2>
        </div>
      </div>

      {requirements.length === 0 ? (
        <div className="document-card">
          <div className="document-card-icon">
            ✓
          </div>

          <h3>
            No additional documents identified
          </h3>

          <p>
            The available official information
            does not specify any additional
            document that needs to be uploaded
            for this scheme.
          </p>
        </div>
      ) : (
        <div className="document-list">
          {requirements.map(
            (requirement, index) => {
              const result = results[index];
              const error = errors[index];
              const verification =
                result?.verification;

              return (
                <div
                  className="document-card"
                  key={`${requirement.name}-${index}`}
                >
                  <div className="document-card-top">
                    <div>
                      <span className="document-number">
                        {String(index + 1).padStart(
                          2,
                          "0"
                        )}
                      </span>

                      <h3>
                        {requirement.name}
                      </h3>

                      <span className="requirement-badge">
                        {getRequirementLabel(
                          requirement.action
                        )}
                      </span>
                    </div>
                  </div>

                  <div className="requirement-details">
                    <p>
                      <strong>
                        What is needed
                      </strong>
                    </p>

                    <p>
                      {
                        requirement.exact_description
                      }
                    </p>
                  </div>

                  <div className="requirement-condition">
                    <strong>
                      Condition
                    </strong>

                    <span>
                      {requirement.condition ||
                        "Always required"}
                    </span>
                  </div>

                  {requirement.action ===
                    "upload" && (
                    <div className="upload-area">
                      <label
                        className={`upload-button ${
                          uploadingIndex === index
                            ? "uploading"
                            : ""
                        }`}
                      >
                        <input
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          disabled={
                            uploadingIndex ===
                            index
                          }
                          onChange={(event) =>
                            handleFileUpload(
                              event.target.files?.[0],
                              requirement,
                              index
                            )
                          }
                        />

                        {uploadingIndex === index
                          ? "Uploading and verifying..."
                          : result
                          ? "Upload another file"
                          : "Choose document"}
                      </label>

                      <p className="upload-help">
                        PDF, PNG, JPG or JPEG
                      </p>
                    </div>
                  )}

                  {requirement.action ===
                    "provide_information" && (
                    <div className="information-only-box">
                      <span className="info-icon">
                        i
                      </span>

                      <div className="information-content">
                        <strong>
                          No file upload required
                        </strong>

                        <p>
                          This requirement should
                          be entered or provided as
                          information during the
                          application process.
                        </p>

                        <label className="information-input-label">
                          {requirement.name}
                        </label>

                        <input
                          type="text"
                          className="information-input"
                          placeholder={`Enter ${requirement.name}`}
                          value={
                            providedInformation[
                              index
                            ] || ""
                          }
                          onChange={(event) => {
                            setProvidedInformation(
                              (previous) => ({
                                ...previous,
                                [index]:
                                  event.target.value,
                              })
                            );
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {requirement.action ===
                    "conditional" && (
                    <div className="conditional-box">
                      <span className="info-icon">
                        !
                      </span>

                      <div>
                        <strong>
                          Conditional requirement
                        </strong>

                        <p>
                          This requirement only
                          applies when the stated
                          condition is applicable
                          to your case.
                        </p>
                      </div>
                    </div>
                  )}

                  {error && (
                    <div className="verification-result verification-error">
                      <div className="verification-icon">
                        !
                      </div>

                      <div>
                        <h4>
                          Upload failed
                        </h4>

                        <p>{error}</p>
                      </div>
                    </div>
                  )}

                  {verification && (
                    <div
                      className={`verification-result ${
                        verification.verified
                          ? "verification-success"
                          : "verification-failed"
                      }`}
                    >
                      <div className="verification-icon">
                        {verification.verified
                          ? "✓"
                          : "!"}
                      </div>

                      <div className="verification-content">
                        <h4>
                          {getVerificationTitle(
                            verification
                          )}
                        </h4>

                        {verification.verified ? (
                          <p>
                            The uploaded document
                            matches the information
                            provided for this
                            requirement.
                          </p>
                        ) : (
                          <>
                            <p>
                              The uploaded document
                              could not be fully
                              verified.
                            </p>

                            {verification.expected_document && (
                              <div className="verification-detail">
                                <span>
                                  Expected
                                </span>

                                <strong>
                                  {
                                    verification.expected_document
                                  }
                                </strong>
                              </div>
                            )}

                            {verification.detected_document && (
                              <div className="verification-detail">
                                <span>
                                  Detected
                                </span>

                                <strong>
                                  {
                                    verification.detected_document
                                  }
                                </strong>
                              </div>
                            )}

                            {verification
                              .mismatches
                              ?.length >
                              0 && (
                              <div className="mismatch-list">
                                <strong>
                                  Problems found
                                </strong>

                                {verification.mismatches.map(
                                  (
                                    mismatch,
                                    mismatchIndex
                                  ) => (
                                    <div
                                      className="mismatch-item"
                                      key={`${mismatch.field}-${mismatchIndex}`}
                                    >
                                      {getMismatchMessage(
                                        mismatch
                                      )}
                                    </div>
                                  )
                                )}
                              </div>
                            )}
                          </>
                        )}

                        {result?.extracted_data && (
                          <details className="ocr-details">
                            <summary>
                              View extracted document
                              information
                            </summary>

                            <div className="ocr-data">
                              {result
                                .extracted_data
                                .name && (
                                <div>
                                  <span>
                                    Name
                                  </span>

                                  <strong>
                                    {
                                      result
                                        .extracted_data
                                        .name
                                    }
                                  </strong>
                                </div>
                              )}

                              {result
                                .extracted_data
                                .income !==
                                undefined &&
                                result
                                  .extracted_data
                                  .income !==
                                  null && (
                                  <div>
                                    <span>
                                      Income
                                    </span>

                                    <strong>
                                      {formatCurrency(
                                        result
                                          .extracted_data
                                          .income
                                      )}
                                    </strong>
                                  </div>
                                )}
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            }
          )}
        </div>
      )}

      <div className="documents-footer">
        <button
          className="primary-button"
          onClick={handleContinue}
        >
          Continue to application draft
        </button>
      </div>
    </div>
  );
}