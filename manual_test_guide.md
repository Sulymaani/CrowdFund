# Manual Testing Guide for Image Upload Size Limits

This guide will help you test the new image upload size and dimension limits that have been implemented.

## Image Upload Limits Overview

| Image Type | Max Size | Max Dimensions | Formats |
|------------|----------|----------------|---------|
| Profile Picture | 1 MB | 512x512 px | JPEG, PNG |
| Organisation Logo | 2 MB | 800x800 px | JPEG, PNG, SVG |
| Organisation Banner | 3 MB | 1920x480 px | JPEG, PNG |
| Campaign Cover | 5 MB | 1920x1080 px | JPEG, PNG |

## Manual Test Cases

### Test Case 1: Organisation Logo Upload - Valid

1. Log in as an organization owner
2. Go to Settings page (`/org/settings/?edit=true`)
3. Prepare a valid logo (JPG/PNG under 2MB, less than 800x800 px)
4. Upload the logo via the form
5. Submit the form
6. **Expected Result:** Logo uploads successfully and displays on the profile page

### Test Case 2: Organisation Logo Upload - Invalid Size

1. Log in as an organization owner
2. Go to Settings page (`/org/settings/?edit=true`)
3. Prepare an invalid logo (over 2MB)
4. Upload the logo via the form
5. Submit the form
6. **Expected Result:** Form submission fails with clear error message about size limit

### Test Case 3: Organisation Logo Upload - Invalid Dimensions

1. Log in as an organization owner
2. Go to Settings page (`/org/settings/?edit=true`)
3. Prepare an invalid logo (over 800x800 px)
4. Upload the logo via the form
5. Submit the form
6. **Expected Result:** Form submission fails with clear error message about dimension limits

### Test Case 4: Organisation Banner Upload - Valid

1. Log in as an organization owner
2. Go to Settings page (`/org/settings/?edit=true`)
3. Prepare a valid banner (JPG/PNG under 3MB, less than 1920x480 px)
4. Upload the banner via the form
5. Submit the form
6. **Expected Result:** Banner uploads successfully and displays on the profile page

### Test Case 5: Campaign Cover Image - Valid

1. Log in as an organization owner
2. Start creating a new campaign (`/org/campaign/new/`)
3. Prepare a valid cover image (JPG/PNG under 5MB, less than 1920x1080 px)
4. Upload the cover image via the form
5. Submit the form
6. **Expected Result:** Campaign creates successfully with the cover image

### Test Case 6: Campaign Cover Image - Invalid Size

1. Log in as an organization owner
2. Start creating a new campaign (`/org/campaign/new/`)
3. Prepare an invalid cover image (over 5MB)
4. Upload the cover image via the form
5. Submit the form
6. **Expected Result:** Form submission fails with clear error message about size limit

### Test Case 7: Profile Picture - Valid

1. Log in as any user
2. Go to user profile settings page
3. Prepare a valid profile picture (JPG/PNG under 1MB, less than 512x512 px)
4. Upload the profile picture via the form
5. Submit the form
6. **Expected Result:** Profile picture uploads successfully and displays in a circular format on the profile page

### Test Case 8: Profile Picture - Invalid Format

1. Log in as any user
2. Go to user profile settings page
3. Prepare an invalid profile picture (e.g., try to upload a GIF or WEBP format)
4. Upload the profile picture via the form
5. Submit the form
6. **Expected Result:** Form submission fails with clear error message about supported formats

## Testing Resources

### How to Create Test Images of Specific Sizes

#### Method 1: Using online tools
- Visit [Canva](https://www.canva.com/) or [Pixlr](https://pixlr.com/) to create images with exact dimensions
- Export as JPEG or PNG

#### Method 2: Using command line (ImageMagick)
```
# Create a 1920x1080 test image
convert -size 1920x1080 xc:blue test_campaign_cover.jpg

# Create a 800x800 test image
convert -size 800x800 xc:red test_logo.png
```

### Creating Test Files of Specific Sizes

#### Method 1: Using online tools
- Use [GenerateBytes](https://www.generatebytes.com/) to create files of exact size
- Rename the extension to .jpg or .png for testing

#### Method 2: Using command line
```
# Create a 2.5MB file
dd if=/dev/zero of=test_file_2_5mb.jpg bs=1M count=2.5
```

## Expected Error Messages

When validation fails, you should see clear error messages such as:
- "File size must not exceed 2 MB. Current size is 2.5 MB."
- "Image width must not exceed 800px. Current width is 900px."
- "Image must be in one of these formats: JPEG, PNG. Current format is GIF."

These error messages should help users understand exactly why their upload failed and what they need to do to correct it.
