#!/usr/bin/env python
#

"""
Test functions for UMFPACK solver. The solver is accessed via spsolve(),
so the built-in SuperLU solver is tested too, in single precision.
"""

import warnings
import nose
from numpy import transpose, array, arange

import random
from numpy.testing import *

from scipy import rand, matrix, diag, eye
from scipy.sparse import csc_matrix, dok_matrix, spdiags, SparseEfficiencyWarning

import scipy
try:
    import scipy.sparse.linalg.dsolve.linsolve as linsolve
except (ImportError, AttributeError):
    raise ImportError( "Cannot import linsolve!" )

warnings.simplefilter('ignore',SparseEfficiencyWarning)

import numpy as nm
try:
    import scikits.umfpack as um
    _have_umfpack = True
except:
    raise Exception('UMFPACK library not found.')
    
# Allow disabling of nose tests if umfpack not present
# See end of file for application
_umfpack_skip = dec.skipif(not _have_umfpack,
                           'UMFPACK appears not to be compiled')

class TestSolvers(TestCase):
    """Tests inverting a sparse linear system"""

    def test_solve_complex_without_umfpack(self):
        """Solve: single precision complex"""
        linsolve.use_solver( useUmfpack = False )
        a = self.a
        a.data = a.data.astype('F',casting='unsafe')
        b = self.b
        b = b.astype('F')
        x = linsolve.spsolve(a, b)
        #print x
        #print "Error: ", a*x-b
        assert_array_almost_equal(a*x, b)


    def test_solve_without_umfpack(self):
        """Solve: single precision"""
        linsolve.use_solver( useUmfpack = False )
        a = self.a.astype('f')
        b = self.b
        x = linsolve.spsolve(a, b.astype('f'))
        #print x
        #print "Error: ", a*x-b
        # single precision: be more generous...
        assert_array_almost_equal(a*x, b, decimal = 5)


    def test_solve_complex_umfpack(self):
        """Solve with UMFPACK: double precision complex"""
        linsolve.use_solver( useUmfpack = True )
        a = self.a.astype('D')
        b = self.b
        x = linsolve.spsolve(a, b)
        #print x
        #print "Error: ", a*x-b
        assert_array_almost_equal(a*x, b)

    def test_solve_umfpack(self):
        """Solve with UMFPACK: double precision"""
        linsolve.use_solver( useUmfpack = True )
        a = self.a.astype('d')
        b = self.b
        x = linsolve.spsolve(a, b)
        #print x
        #print "Error: ", a*x-b
        assert_array_almost_equal(a*x, b)

    def test_solve_sparse_rhs(self):
        """Solve with UMFPACK: double precision, sparse rhs"""
        linsolve.use_solver( useUmfpack = True )
        a = self.a.astype('d')
        b = csc_matrix( self.b.reshape((5,1)) )
        x = linsolve.spsolve(a, b)
        #print x
        #print "Error: ", a*x-b
        assert_array_almost_equal(a*x, self.b)

    def test_factorized_umfpack(self):
        """Prefactorize (with UMFPACK) matrix for solving with multiple rhs"""
        linsolve.use_solver( useUmfpack = True )
        a = self.a.astype('d')
        solve = linsolve.factorized( a )

        x1 = solve( self.b )
        assert_array_almost_equal(a*x1, self.b)
        x2 = solve( self.b2 )
        assert_array_almost_equal(a*x2, self.b2)

    def test_factorized_without_umfpack(self):
        """Prefactorize matrix for solving with multiple rhs"""
        linsolve.use_solver( useUmfpack = False )
        a = self.a.astype('d')
        solve = linsolve.factorized( a )

        x1 = solve( self.b )
        assert_array_almost_equal(a*x1, self.b)
        x2 = solve( self.b2 )
        assert_array_almost_equal(a*x2, self.b2)

    def setUp(self):
        self.a = spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]], [0, 1], 5, 5)
        #print "The sparse matrix (constructed from diagonals):"
        #print self.a
        self.b = array([1, 2, 3, 4, 5])
        self.b2 = array([5, 4, 3, 2, 1])



class TestFactorization(TestCase):
    """Tests factorizing a sparse linear system"""

    def test_complex_lu(self):
        """Getting factors of complex matrix"""
        umfpack = um.UmfpackContext("zi")

        for A in self.complex_matrices:
            umfpack.numeric(A)

            (L,U,P,Q,R,do_recip) = umfpack.lu(A)

            L = L.todense()
            U = U.todense()
            A = A.todense()
            if not do_recip: R = 1.0/R
            R = matrix(diag(R))
            P = eye(A.shape[0])[P,:]
            Q = eye(A.shape[1])[:,Q]

            assert_array_almost_equal(P*R*A*Q,L*U)

    def test_real_lu(self):
        """Getting factors of real matrix"""
        umfpack = um.UmfpackContext("di")

        for A in self.real_matrices:
            umfpack.numeric(A)

            (L,U,P,Q,R,do_recip) = umfpack.lu(A)

            L = L.todense()
            U = U.todense()
            A = A.todense()
            if not do_recip: R = 1.0/R
            R = matrix(diag(R))
            P = eye(A.shape[0])[P,:]
            Q = eye(A.shape[1])[:,Q]

            assert_array_almost_equal(P*R*A*Q,L*U)


    def setUp(self):
        random.seed(0) #make tests repeatable
        self.real_matrices = []
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 1], 5, 5) )
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 1], 4, 5) )
        self.real_matrices.append(spdiags([[1, 2, 3, 4, 5], [6, 5, 8, 9, 10]],
                                          [0, 2], 5, 5) )
        self.real_matrices.append(rand(3,3))
        self.real_matrices.append(rand(5,4))
        self.real_matrices.append(rand(4,5))

        self.real_matrices = [csc_matrix(x).astype('float') for x \
                in self.real_matrices]
        self.complex_matrices = [x.astype('complex')
                                 for x in self.real_matrices]

# Skip methods if umfpack not present
for cls in [TestSolvers, TestFactorization]:
    decorate_methods(cls, _umfpack_skip)

if __name__ == "__main__":
    nose.run(argv=['', __file__])
