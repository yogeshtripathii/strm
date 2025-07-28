import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io

# Set Streamlit page configuration
st.set_page_config(layout="wide", page_title="Data Analysis Dashboard")

st.title("📊 Data Analysis Dashboard")
st.markdown("Upload your CSV or Excel file to get started with basic data analysis and visualizations.")

# File Uploader
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = None
    file_type = uploaded_file.name.split('.')[-1]

    # Try loading with different encodings if UTF-8 fails
    encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    for encoding in encodings_to_try:
        try:
            if file_type == 'csv':
                df = pd.read_csv(uploaded_file, encoding=encoding)
            elif file_type == 'xlsx':
                df = pd.read_excel(uploaded_file)
            st.success(f"File loaded successfully with {encoding} encoding!")
            break
        except UnicodeDecodeError:
            st.warning(f"Failed to decode with {encoding}. Trying next encoding...")
        except Exception as e:
            st.error(f"An error occurred while loading the file with {encoding} encoding: {e}")
            break

    if df is not None:
        st.subheader("Raw Data Preview")
        st.write(df.head())

        st.subheader("Column Information")
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

        st.subheader("Data Types and Conversion")
        st.write("Here you can review the current data types and convert them if necessary.")

        modified_df = df.copy()
        for col in df.columns:
            st.write(f"**Column:** `{col}` - **Current Type:** `{df[col].dtype}`")
            new_type = st.selectbox(f"Convert `{col}` to:",
                                    ['No Change', 'numeric', 'datetime', 'category', 'string'],
                                    key=f"convert_{col}")
            if new_type != 'No Change':
                try:
                    if new_type == 'numeric':
                        modified_df[col] = pd.to_numeric(modified_df[col], errors='coerce')
                    elif new_type == 'datetime':
                        modified_df[col] = pd.to_datetime(modified_df[col], errors='coerce')
                    elif new_type == 'category':
                        modified_df[col] = modified_df[col].astype('category')
                    elif new_type == 'string':
                        modified_df[col] = modified_df[col].astype(str)
                    st.success(f"Successfully converted `{col}` to `{new_type}`.")
                except Exception as e:
                    st.error(f"Could not convert `{col}` to `{new_type}`: {e}")

        st.subheader("Descriptive Statistics for Numerical Columns")
        numerical_cols = modified_df.select_dtypes(include=['number']).columns
        if not numerical_cols.empty:
            st.write(modified_df[numerical_cols].describe())
        else:
            st.info("No numerical columns found for descriptive statistics.")

        st.subheader("Data Visualization")

        plot_type = st.selectbox("Select Plot Type:", ["Bar Plot", "Line Plot", "Histogram", "Scatter Plot", "Pie Chart", "Heatmap"])

        if plot_type == "Bar Plot":
            col_x = st.selectbox("Select X-axis column (Categorical/Numerical):", modified_df.columns, key="bar_x")
            col_y = st.selectbox("Select Y-axis column (Numerical, optional):", ['None'] + list(modified_df.columns), key="bar_y")

            if col_x:
                plt.figure(figsize=(10, 6))
                if col_y != 'None':
                    sns.barplot(x=col_x, y=col_y, data=modified_df)
                    plt.ylabel(col_y)
                else:
                    # If only x is selected, count occurrences
                    sns.countplot(x=col_x, data=modified_df)
                    plt.ylabel("Count")
                plt.title(f"Bar Plot of {col_x} vs {col_y if col_y != 'None' else 'Count'}")
                plt.xlabel(col_x)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(plt)
                plt.clf() # Clear the plot for the next visualization

        elif plot_type == "Line Plot":
            col_x = st.selectbox("Select X-axis column (Numerical/Datetime):", modified_df.columns, key="line_x")
            col_y = st.selectbox("Select Y-axis column (Numerical):", modified_df.select_dtypes(include=['number']).columns, key="line_y")

            if col_x and col_y:
                plt.figure(figsize=(10, 6))
                sns.lineplot(x=col_x, y=col_y, data=modified_df)
                plt.title(f"Line Plot of {col_y} over {col_x}")
                plt.xlabel(col_x)
                plt.ylabel(col_y)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(plt)
                plt.clf()

        elif plot_type == "Histogram":
            col_hist = st.selectbox("Select column for Histogram (Numerical):", modified_df.select_dtypes(include=['number']).columns, key="hist_col")

            if col_hist:
                plt.figure(figsize=(10, 6))
                sns.histplot(modified_df[col_hist], kde=True)
                plt.title(f"Histogram of {col_hist}")
                plt.xlabel(col_hist)
                plt.ylabel("Frequency")
                st.pyplot(plt)
                plt.clf()

        elif plot_type == "Scatter Plot":
            col_x = st.selectbox("Select X-axis column (Numerical):", modified_df.select_dtypes(include=['number']).columns, key="scatter_x")
            col_y = st.selectbox("Select Y-axis column (Numerical):", modified_df.select_dtypes(include=['number']).columns, key="scatter_y")
            col_hue = st.selectbox("Select Hue column (Categorical, optional):", ['None'] + list(modified_df.columns), key="scatter_hue")

            if col_x and col_y:
                plt.figure(figsize=(10, 6))
                if col_hue != 'None':
                    sns.scatterplot(x=col_x, y=col_y, hue=col_hue, data=modified_df)
                else:
                    sns.scatterplot(x=col_x, y=col_y, data=modified_df)
                plt.title(f"Scatter Plot of {col_y} vs {col_x}")
                plt.xlabel(col_x)
                plt.ylabel(col_y)
                st.pyplot(plt)
                plt.clf()

        elif plot_type == "Pie Chart":
            col_pie = st.selectbox("Select column for Pie Chart (Categorical/Numerical):", modified_df.columns, key="pie_col")

            if col_pie:
                plt.figure(figsize=(8, 8))
                # Calculate value counts and take top N, then sum the rest into 'Other'
                value_counts = modified_df[col_pie].value_counts()
                if len(value_counts) > 10: # Limit to top 10 categories for readability
                    top_n = value_counts.head(9)
                    other_sum = value_counts.iloc[9:].sum()
                    if other_sum > 0:
                        top_n['Other'] = other_sum
                    labels = top_n.index
                    sizes = top_n.values
                else:
                    labels = value_counts.index
                    sizes = value_counts.values

                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
                plt.title(f"Pie Chart of {col_pie}")
                plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(plt)
                plt.clf()

        elif plot_type == "Heatmap":
            numerical_cols_for_heatmap = modified_df.select_dtypes(include=['number']).columns
            if not numerical_cols_for_heatmap.empty:
                st.write("Heatmap of Correlation Matrix for Numerical Columns")
                plt.figure(figsize=(10, 8))
                corr_matrix = modified_df[numerical_cols_for_heatmap].corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
                plt.title("Correlation Heatmap")
                st.pyplot(plt)
                plt.clf()
            else:
                st.info("No numerical columns available to generate a Heatmap.")

else:
    st.info("Please upload a CSV or Excel file to begin your analysis.")

