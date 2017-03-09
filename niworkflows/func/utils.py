import csv
import math
import os
import sys

from errno import EEXIST

from nipype.interfaces.base import (BaseInterface, BaseInterfaceInputSpec, File,
                                    OutputMultiPath, TraitedSpec)
from nipype.utils.filemanip import split_filename

class Ants2FSLInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, desc='ANTS style motion parameters to convert',
                   mandatory=True)

class Ants2FSLOutputSpec(TraitedSpec):
    mat_file = OutputMultiPath(File(exists=True), desc="transformation matrices")
    par_file = File(exists=True, desc="text-file with motion parameters")

class Ants2FSL(BaseInterface):
    ''' Take antsMotionCorr motion output as input, convert to FSL style
        mat files'''
    input_spec = Ants2FSLInputSpec
    output_spec = Ants2FSLOutputSpec

    def _run_interface(self, runtime):
        in_file = self.inputs.in_file
        _, base, in_fname = split_filename(in_file)
        par_out = os.path.join(base, in_fname + '.par')

        base = os.path.join(base, 'mats')

        try:
            os.makedirs(base)
        except OSError as exc:
            if exc.errno == EEXIST:
                pass

        in_data = csv.reader(open(in_file))
        # first line is a header, lets skip it.
        next(in_data)
        par_line = "{:.8f}, {:.8f}, {:.8f}, {:.8f}, {:.8f}, {:.8f}\n"
        mat_line = "{:.8f} {:.8f} {:.8f} {:.8f}\n"
        i = 0
        for x in in_data:
            fname = "MAT_{0:04d}".format(i)
            t1 = math.atan2(float(x[7]), float(x[10]))
            c2 = math.sqrt((float(x[2]) * float(x[2])) + (float(x[3]) * float(x[3])))
            t2 = math.atan2(-float(x[4]), c2)
            t3 = math.atan2(float(x[3]), float(x[2]))
            par_out.write(par_line.format(t1, t2, t3, float(x[11]), float(x[12]), float(x[13])))
            mat_out = open(os.path.join(base, fname), 'w+')
            mat_out.write(mat_line.format(float(x[2]), float(x[3]), float(x[4]), float(x[11])))
            mat_out.write(mat_line.format(float(x[5]), float(x[6]), float(x[7]), float(x[12])))
            mat_out.write(mat_line.format(float(x[8]), float(x[9]), float(x[10]), float(x[13])))
            mat_out.write(mat_line.format(0, 0, 0, 1))
            mat_out.close()
            i += 1
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        return outputs