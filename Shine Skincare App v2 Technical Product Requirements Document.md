# Shine Skincare App v2 Technical Product Requirements Document

## 1. Introduction

This document outlines the technical requirements for version 2 of the Shine Skincare application, focusing on a pivot from medical to cosmetic skin analysis using 100% synthetic faces. The primary goal is to enhance the user experience with a full-screen camera interface optimized for mobile, similar to Snapchat, and to drive product recommendations based on cosmetic skin analysis. The application will leverage synthetic faces for analysis and normalization, with results presented using a gender-neutral, dark-mode-enabled interface.

## 2. Goals and Objectives

The primary goal of Shine Skincare App v2 is to provide personalized cosmetic skincare product recommendations based on AI-powered analysis of user-submitted facial images. To achieve this, several key objectives have been established. First, the application will implement a full-screen camera interface optimized for mobile devices, ensuring a seamless and intuitive user experience. Second, the underlying AI analysis model will transition from medical to purely cosmetic skin conditions. Third, the application will exclusively utilize 100% synthetic faces for all analysis, including baseline normalization, with these synthetic faces varying by demographic. Fourth, analysis results will be presented through a gender-neutral, dark-mode-enabled interface, categorizing cosmetic concerns as mild, moderate, or severe. Finally, the application will prioritize product recommendations as the primary outcome of the analysis.

## 3. User Stories

Users of the Shine Skincare App v2 will be able to capture their face using a full-screen mobile camera interface and receive a cosmetic skin analysis based on the captured image. They will understand their skin condition through gender-neutral categorizations of mild, moderate, or severe for various cosmetic concerns. The application will provide personalized product recommendations tailored to their specific cosmetic skin analysis results, which will be viewed in a clear, intuitive, and dark-mode-enabled interface. Crucially, the user's skin analysis will be normalized against synthetic baseline faces that vary by demographic, such as age and skin tone.

## 4. Technical Architecture

### 4.1. Frontend (Mobile-First, Snapchat-like GUI)

The frontend will be built upon the existing Next.js with React framework and styled using Tailwind CSS and Radix UI, ensuring comprehensive dark mode support. A custom full-screen camera view will be implemented, featuring real-time face detection and cropping, optimized for mobile portrait orientation to emulate the simplicity and speed of social media camera interfaces like Snapchat. The user interface will emphasize intuitive, gesture-driven navigation with minimal clicks and clear visual feedback, and all UI elements must adhere to gender-neutral design principles. State management will continue to utilize React Context for handling analysis flow, user preferences, and product recommendations, while Google OAuth via Supabase will manage authentication.

### 4.2. Backend (AI/ML Services)

The backend will maintain its Python Flask with gunicorn framework. Computer vision capabilities, leveraging OpenCV and MediaPipe, will be used for enhanced facial landmark detection and image preprocessing. The core machine learning model, built with TensorFlow/Keras, will be retrained or adapted to focus exclusively on cosmetic skin conditions such as texture, tone evenness, pore visibility, fine lines, and hydration indicators, rather than medical conditions. The model's input will be preprocessed facial images, and its output will include cosmetic condition percentages and severity (mild/moderate/severe) for each identified concern. The application will integrate with the Google Gemini API (or a similar service) for on-demand generation of diverse synthetic faces, which will be used for dynamic normalization and potentially for future model training, building upon the existing `syntheticfaces` repository. A dedicated normalization service will compare a user's analyzed face against a dynamically generated or pre-selected set of synthetic healthy faces, stratified by relevant demographics (age group, skin tone, gender). Finally, the existing product recommendation engine will be enhanced to prioritize cosmetic product suggestions based on the new cosmetic analysis results and severity levels.

### 4.3. Data

The existing `syntheticfaces` repository will serve as the foundational synthetic face dataset. This dataset will be expanded as needed with additional synthetic faces generated via the Google Gemini API to ensure comprehensive demographic representation across age, skin tone, and gender for robust normalization. It is a strict requirement that all faces used for analysis and normalization must be 100% synthetic. A clear ontology for cosmetic skin conditions, including texture, tone evenness, pore visibility, fine lines, and hydration indicators, will be defined along with their corresponding mild, moderate, and severe classifications to guide both model training and result presentation. The product database will be maintained and expanded with metadata relevant to cosmetic concerns to facilitate precise recommendations.

## 5. Key Features

The application will feature a full-screen mobile camera for fast and intuitive facial image capture. AI-powered cosmetic analysis will provide real-time assessment of skin concerns, categorizing them into mild, moderate, or severe. Personalized product recommendations will be tailored to individual analysis results. Demographic-aware normalization will compare user skin against synthetic healthy baselines matching their demographic profile. All aspects of the UI/UX, language, and synthetic faces will adhere to a gender-neutral design, and the application will offer full support for dark mode preferences.

## 6. Open Questions & Future Considerations

Several considerations remain for future refinement. The optimal number of synthetic healthy faces per demographic group for robust normalization needs to be determined; this could range from 10-20 for an MVP, 100+ for statistical robustness, or 500+ for diverse representation. A detailed list of specific cosmetic conditions to be analyzed (e.g., fine lines, texture, tone, hydration, pore visibility, redness, hyperpigmentation) and their precise definitions for mild/moderate/severe categorization is required. Furthermore, a strategy for collecting and utilizing user feedback on product recommendations or analysis accuracy to improve the AI model and recommendation engine needs to be established. Finally, despite the use of synthetic faces, specific privacy and security protocols for handling user images (even if not stored long-term) and analysis data must be clearly defined.

## 7. Success Metrics

Success will be measured by increased user engagement with the camera analysis feature, a higher conversion rate from analysis to product recommendation views and purchases, and positive user satisfaction feedback regarding the accuracy of cosmetic analysis and the relevance of product recommendations. A key performance metric will be a fast analysis processing time, targeting under 5 seconds.

## 8. Deployment

The frontend will be deployed via AWS Amplify, leveraging GitHub for continuous deployment. The backend, hosting the AI/ML inference and API, will utilize AWS Elastic Beanstalk or a similar scalable AWS service. Supabase PostgreSQL will serve as the database for user data and the product catalog, while AWS S3 will be used for storing synthetic face datasets and for temporary image processing.

## 9. Next Steps

Immediate next steps include finalizing the specific cosmetic conditions and their mild/moderate/severe definitions, and determining the optimal number of synthetic healthy faces required for demographic-aware normalization. Concurrently, detailed UI/UX wireframes for the full-screen camera and results presentation should be developed. Following these foundational steps, development of the cosmetic-focused AI model and its integration with the synthetic face generation API can commence.

