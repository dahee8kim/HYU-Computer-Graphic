<h1>Ray Tracer</h1>
<h2>Reference</h2>
- <a href="http://calab.hanyang.ac.kr/courses/CG_taesoo/PA1_2019.pdf" target="_blank">calab.hanyang.ac.kr</a><br>
- <a href="http://www.cs.cornell.edu/courses/cs4620/2011fa/lectures/07raytracingWeb.pdf" target="_blank">cs.cornell.edu</a><br>
- <a href="http://web.cse.ohio-state.edu/~shen.94/681/Site/Slides_files/basic_algo.pdf">web.cse.ohio-state.edu</a><br>
<br>
<hr>
<br>
<h1>Program 1: ray tracer</h1>
<i>out: Thursday March 21, 2019<br>
due: Thursdsay April 25, 2019 (24pm)</i>
<br>
<h2>1. Overview</h2>
Ray tracing is a simple and powerful algorithm for rendering images. Within the accuracy of the scene and shading models and with enough computing time, the images produced by a ray tracer can be physically accurate and can appear indistinguishable from real images. Your ray tracer will not be able to produce physically accurate images though.<br>
<br>
In this assignment, your ray tracer will have support for:<br>
• Spheres and axis-aligned boxes<br>
• Lambertian and Phong shading<br>
• Point lights with shadows<br>
• Arbitrary perspective cameras<br>
<br>
Some framework code (rayTracer.py - less than 60 lines) is provided to save you the time to implement I/0, an XML parser, and vector operations.<br>
<br>
However, the framework does not contain any code that does any actual ray tracing—you will develop that code yourself.<br>
<br>
When you write the ray tracing code, you have the freedom to determine the design you believe is best. You may want to add some classes to the program, and there are many choices about where to put the various parts of the computation. Any solution that correctly meets the requirements below and is clearly written will receive full credit. Results without any shading at all will still receive 80% of the full credit to encourage submission. The textbook, the lectures, and the course staff (including the professor) are all sources of information about good approaches to coding up a ray tracer.<br>
<br>
This is not to say that you need to write a lot of new code. For reference, the framework contains about 60 lines of code, and our solution contains three small additional classes and about 200 additional lines of code.<br>
<br>
<br>
<h2>2. Requirements</h2>
1. Use a ray tracing algorithm.<br>
2. Support arbitrary perspective projections as described in the file format section below.<br>
3. Support spheres and axis-aligned boxes.<br>
4. Support the Lambertian and Blinn-Phong shading models, as defined in Shirley 9.1–9.2 and in the lecture notes.<br>
5. Support point lights that provide illumination that does not fall off with distance.<br>
<br>
You do not need to worry about malformed input, either syntactically or semantically. For instance, you will not be given a sphere with a negative radius or a scene without a camera.<br>
<br>
<br>
<h2>3. File format</h2>
The input file for your ray tracer is in XML. An XML file contains sequences of nested elements that are delimited by HTML-like angle-bracket tags. For instance, the XML code:<br>
<br>

```xml
<scene>
<camera>
</camera>
<surface type=Sphere>
<center>1.0 2.0 3.0</center>
</surface>
</scene>
```

contains four elements. One is a scene element that contains two others, called camera and surface. The surface element has an attribute named type that has the value Sphere. It also contains a center element that contains the text “1.0 2.0 3.0”, which in this context would be interpreted as the 3D point (1, 2, 3). An input file for the ray tracer always contains one scene element, which is allowed to contains tags of the following types:<br>
<br>
• surface: This element describes a geometric object. It must have an attribute type with value Sphere or Box. It can contain a shader element to set the shader, and also geometric parameters depending on its type:<br>
– for sphere: center, containing a 3D point, and radius, containing a real number.<br>
– for box: minPt and maxPt, each containing a 3D point. If the two points are (xmin , ymin , zmin) and (xmax , ymax , zmax ) then the box is [xmin , xmax ] × [ymin , ymax ] × [zmin , zmax ].<br>
<br>
• camera: This element describes the camera. It is described by the following elements:<br>
– viewPoint, a 3D point that specifies the center of projection.<br>
– viewDir, a 3D vector that specifies the direction toward which the camera is looking. Its magnitude is not used.<br>
– viewUp, a 3D vector that is used to determine the orientation of the image.<br>
– projNormal, a 3D vector that specifies the normal to the projection plane. Its magnitude is not used, and negating its direction has no effect. By default it is equal to the view direction.<br>
– projDistance, a real number d giving the distance from the center of the image rectangle to the center of projection.<br>
– viewWidth and viewHeight, two real numbers that give the dimensions of viewing window on the image plane.<br>
The camera’s view is determined by the center of projection (the viewpoint) and a view window of size viewWidth by viewHeight. The window’s center is positioned along the view direction at a distance d from the viewpoint. It is oriented in space so that it is perpendicular to the image plane normal and its top and bottom edges are perpendicular to the up vector.<br>
<br>
• image: This element is just a pair of integers that specify the size of the output image in pixels.<br>
<br>
• light: This element describes a light. It contains the 3D point position and the RGB color color.<br>
<br>
• shader: This element describes how a surface should be shaded. It must have an attribute type with value Lambertian or Phong. The Lambertian shader uses the RGB color diffuseColor, and the Phong shader additionally uses the RGB color specularColor and the real number exponent. A shader can appear inside a surface element, in which case it applies to that surface. It can also appear directly in the scene, which is useful if you want to give it a name and refer to it later from inside a surface (see below). If the same object needs to be referenced in several places, for instance when you want to use one shader for many surfaces, you can use the attribute name to give it a name, then later include a reference to it by using the attribute ref.<br>
<br>
For instance:<br>

```xml
<shader type="Lambertian" name="gray">
<diffuseColor>0.5 0.5 0.5</diffuseColor>
</shader>
<surface type="Sphere">
<center>0 0 0</center>
<shader ref="gray"/>
</surface>
<surface type="Sphere">
<center>5 0 0</center>
<shader ref="gray"/>
</surface>
```

applies the same shader to two spheres. Really, the file format is very simple and from the examples we provide you should have no trouble constructing any scene you want.<br>
<br>
<br>
<h2>4. Framework</h2>
The framework for this assignment includes a simple main program, some examples for basic image processing and parsing for the input file format.<br>
<br>
<h3>4.1 Parser</h3>
The framework utilizes Python’s built-in XML parsing. The parser simply reads a XML document and instantiates an object for each XML entity, adding it to its containing element.<br>
<br>
For instance, the input<br>
<br>

```xml
<scene>
<surface type="Sphere">
<shader type="Lambertian">
<diffuseColor>0 0 1</diffuseColor>
</shader>
<center>1 2 3</center>
<radius>4</radius>
</surface>
</scene>
```

results in a parse tree which are automatically generated from the parser. There is more detail for the curious in the rayTracer.py.<br>
The practical result of all this is that your ray tracer is handed a scene that contains objects that are in one-to-one correspondence with the elements in the input file. You only need to use the information that is already there.<br>
<br>
<h3>4.2. rayTracer.py</h3>
The main method holds the entry point for the program. The main method is provided, so that your program will have an command-line interface compatible with ours. It treats each command line argument as the name of an input file, which it parses, renders an image, and writes the image to a PNG file. You need to write some additional code to do the actual rendering.<br>
<br>
<h3>4.3 Image</h3>
The framework creates an array of floats and provide the requisite code to set pixels and to output the image to a PNG file.<br>
<br>
<h3>4.4 The Color class</h3>
The framework contains a class to represent RGB colors. It supports gamma correction.<br>
<br>
<br>
<h2>5. Submission and FAQ</h2>
<h3>5.1. How to run the skeleton code</h3>
After installing the necessary packages (python3, pil and numpy), unpack the zip file.<br>
<br>
Then run:<br>
<code>python3 rayTracer.py scenes/one-sphere.xml</code><br>
<br>
This will render to a PNG file of the same name, but with a ".png" extension.<br>
The supposed output files are already in the folder, and the above command will overwrite the scenes/one-sphere.xml.png file with a mostly empty image.<br>
<br>
<h3>5.2. Notice</h3>
Submission will be through the course git repository. A FAQ page will be uploaded on the course website detailing any new questions and their answers brought to the attention of the course staff.
