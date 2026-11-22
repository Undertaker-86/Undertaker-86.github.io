/**
 * Personal details. Everything that identifies or contacts the owner is OFF until the owner approves it.
 * Flip a flag to publish that item; the site renders cleanly either way.
 */
export const site = {
  name: 'Gyan Edbert Zesiro',
  shortName: 'Gyan Zesiro',
  positioning: 'Robotics engineer: learning-based control, perception and embedded systems',
  description:
    'Portfolio of Gyan Edbert Zesiro, M.Sc. Robotics, Systems and Control student at ETH Zurich: humanoid RL, perception, planning and embedded control.',
  location: 'Zurich, Switzerland',

  // ---- contact: only items with show: true are published ----
  email: { show: true, value: 'gyan.gyan26@gmail.com' },
  phone: { show: false, value: '' }, // default: never shown
  linkedin: { show: false, value: '' },
  github: { show: false, value: '' },
  photo: { show: false },
  scholar: { show: true, href: 'https://scholar.google.com/citations?user=eKzf9uoAAAAJ&hl=en' },
};

export const education = [
  {
    school: 'ETH Zurich',
    degree: 'M.Sc. Robotics, Systems and Control',
    dates: 'Sep 2026 – Mar 2028 (expected)',
    place: 'Zurich, Switzerland',
    detail:
      'Robot Dynamics · Planning and Decision Making for Autonomous Robots · Vision Algorithms for Mobile Robotics · CV & AI for Autonomous Cars · Embedded Control Systems · Model Predictive Control · Recursive Estimation · Dynamic Programming and Optimal Control',
  },
  {
    school: 'University of British Columbia',
    degree: 'B.A.Sc. Mechanical Engineering, Mechatronics Option',
    dates: 'Aug 2022 – May 2026',
    place: 'Vancouver, Canada',
    detail: 'Graduated with Distinction (Cum Laude), cumulative GPA 91.8 %.',
  },
];

export const roles = [
  { org: 'NomadZ RoboCup Team, ETH Zurich', role: 'Motion Control & Robot Learning', dates: 'Sep 2026 – present', project: 'nomadz-kicking' },
  { org: 'SimPL Biomedical Sensing Lab, UBC', role: 'Machine Learning Engineer', dates: 'Sep 2025 – Jun 2026', project: 'header-net' },
  { org: 'Airbus Robotics', role: 'Capstone Technical Manager', dates: 'Sep 2025 – Apr 2026' },
  { org: 'Stoeber Lab, UBC', role: 'Computer Vision Engineer', dates: 'Jan 2025 – Sep 2025', project: 'stoeber-porous-valve' },
  { org: 'SimPL Biomedical Sensing Lab, UBC', role: 'DSP Student Assistant', dates: 'Apr 2024 – Aug 2024', project: 'stethoscope' },
  { org: 'MEMS Lab, UBC', role: 'Research Assistant', dates: 'Nov 2023 – Apr 2025' },
  { org: 'UBC Subbots', role: 'Control Systems Lead', dates: 'Aug 2023 – Dec 2025', project: 'subbots' },
];

export const publications = [
  {
    authors: 'P. D. S. H. Gunawardane, G. E. Zesiro, H. Zhou, G. Alici, M. Chiao',
    title: 'Programmable Variable-Stiffness Multilayer Elastomer Composites With High-Aspect-Ratio Low-Melting-Point Alloys',
    venue: 'Advanced Materials Technologies',
    year: '2026',
    href: 'https://doi.org/10.1002/admt.71286',
  },
  {
    authors: 'Y. Cheng, G. E. Zesiro, S. Ma, B. Stoeber',
    title: 'A Self-Regulating Microfluidic Valve Based on Deformable Porous Media',
    venue: 'IEEE MEMS 2026, Salzburg',
    year: '2026',
    href: 'https://ieeexplore.ieee.org/document/11419604',
    project: 'stoeber-porous-valve',
  },
  {
    authors: 'Y. Cheng, G. E. Zesiro, B. Stoeber',
    title: 'Characterizing the Poroelastic Time Scale of a Poroviscoelastic Medium using Indentation Tests',
    venue: 'APS DFD 2025, Houston',
    year: '2025',
    href: 'https://meetings-archive.aps.org/dfd/2025/c33/1/',
    project: 'stoeber-porous-valve',
  },
  {
    authors: 'P. D. S. H. Gunawardane, G. E. Zesiro, P. Cheung, H. Zhou, G. Alici, M. Chiao',
    title: 'Active Tip Trajectory Control in Zig-Zag Soft Actuators using Modular Strain-Limiting Layers with Phase-Changing Inclusions',
    venue: 'IEEE-RAS RoboSoft 2025, Lausanne',
    year: '2025',
    href: 'https://ieeexplore.ieee.org/document/11020945',
  },
];

export const skills: Record<string, string> = {
  'ML & robotics': 'PyTorch, Isaac Lab / Isaac Sim, MuJoCo, ROS 2, Nav2, SLAM, Gazebo, OpenCV, Optuna',
  Languages: 'Python, C, C++, MATLAB, Rust, SQL, Verilog/VHDL, TypeScript',
  'Embedded & electronics': 'NVIDIA Jetson, microcontrollers (S32K144, Teensy, RP2040), CAN, PCB design (Altium/KiCad), PLC, FPGA',
  'Mechanical & simulation': 'SolidWorks, Abaqus, Ansys, COMSOL, Simulink/Stateflow, machining, 3D printing, sheet metal',
};
