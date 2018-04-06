"""Graph database schema."""

from goblin import Property
from goblin import VertexProperty
import goblin.properties as properties

from thoth.common import datetime_str2timestamp

from .models_base import VertexBase
from .models_base import EdgeBase


class Package(VertexBase):
    """Package vertex in the graph representing a package without version."""

    ecosystem = VertexProperty(properties.String)
    name = VertexProperty(properties.String)


class RPMRequirement(VertexBase):
    """Requirement of an RPM as stated in a spec file."""

    name = VertexProperty(properties.String)


class PackageVersionBase(VertexBase):
    """Package-version vertex in the graph representing any versioned package."""

    ecosystem = VertexProperty(properties.String)
    name = VertexProperty(properties.String)
    version = VertexProperty(properties.String)

    @classmethod
    def construct(cls, *args, **kwargs):
        raise NotImplementedError


class RPMPackageVersion(PackageVersionBase):
    """RPM-specific package version."""

    release = VertexProperty(properties.String)
    epoch = VertexProperty(properties.String)
    arch = VertexProperty(properties.String)
    src = VertexProperty(properties.Boolean)
    package_identifier = VertexProperty(properties.String)

    @classmethod
    def construct(cls, package_info: dict):
        """Construct an RPM package-version vertex based on analyzer result entry."""
        return cls.from_properties(
            ecosystem='rpm',
            name=package_info['name'],
            version=package_info['version'],
            release=package_info.get('release'),
            epoch=package_info.get('epoch'),
            arch=package_info.get('arch'),
            src=package_info.get('src', False),
            package_identifier=package_info.get('package_identifier', package_info['name'])
        )


class PythonPackageVersion(PackageVersionBase):
    """Python package version vertex."""

    @classmethod
    def construct(cls, package_info):
        """Construct a Python package-version vertex based on analyzer result entry."""
        return cls.from_properties(
            ecosystem=package_info['ecosystem'],
            name=package_info['result']['name'],
            version=package_info['result']['version'],
        )


class RuntimeEnvironment(VertexBase):
    """Environment such as container image which consists of various packages."""

    image = VertexProperty(properties.String)
    # TODO: capture hashes of layers

    analysis_datetime = VertexProperty(properties.Integer)
    analysis_document_id = VertexProperty(properties.String)
    analyzer = VertexProperty(properties.String)
    analyzer_version = VertexProperty(properties.String)

    @classmethod
    def from_document(cls, analysis_document: dict):
        return cls.from_properties(
            image=analysis_document['metadata']['arguments']['extract-image']['image'],
            analysis_datetime=datetime_str2timestamp(analysis_document['metadata']['datetime']),
            analysis_document_id=analysis_document['metadata']['hostname'],
            analyzer=analysis_document['metadata']['analyzer'],
            analyzer_version=analysis_document['metadata']['analyzer_version']
        )


class SoftwareStack(VertexBase):
    """Observations we have about the given stack."""

    # TODO: add observation info

    analysis_document_id = VertexProperty(properties.String)
    analysis_datetime = VertexProperty(properties.Integer)
    analyzer = VertexProperty(properties.String)
    analyzer_version = VertexProperty(properties.String)

    @classmethod
    def from_document(cls, analysis_document: dict):
        return cls.from_properties(
            analysis_datetime=datetime_str2timestamp(analysis_document['metadata']['datetime']),
            analysis_document_id=analysis_document['metadata']['hostname'],
            analyzer=analysis_document['metadata']['analyzer'],
            analyzer_version=analysis_document['metadata']['analyzer_version']
        )


class DependsOn(EdgeBase):
    """Dependency between packages modeling based on ecosystem specification."""

    version_range = Property(properties.String, default='*')
    package_name = Property(properties.String)
    extras = Property(properties.String)


class IsPartOf(EdgeBase):
    """Connection to environment."""


class IsSolvedBy(EdgeBase):
    """Connection whether the given package is installable into environment."""

    solver_document_id = Property(properties.String)
    solver = Property(properties.String)
    solver_version = Property(properties.String)
    solver_datetime = Property(properties.Integer)

    installable = Property(properties.Boolean)

    @classmethod
    def from_document(cls, solver_document: dict):
        return cls.from_properties(
            solver_datetime=datetime_str2timestamp(solver_document['metadata']['datetime']),
            solver_document_id=solver_document['metadata']['hostname'],
            solver=solver_document['metadata']['analyzer'],
            solver_version=solver_document['metadata']['analyzer_version']
        )


class Requires(EdgeBase):
    """Requirement edge of an RPM package."""

    analysis_document_id = Property(properties.String)
    analysis_datetime = Property(properties.Integer)
    analyzer = Property(properties.String)
    analyzer_version = Property(properties.String)

    @classmethod
    def from_document(cls, source, target, analysis_document):
        return cls.from_properties(
            source=source,
            target=target,
            analysis_datetime=datetime_str2timestamp(analysis_document['metadata']['datetime']),
            analysis_document_id=analysis_document['metadata']['hostname'],
            analyzer=analysis_document['metadata']['analyzer'],
            analyzer_version=analysis_document['metadata']['analyzer_version']
        )


class CreatesStack(EdgeBase):
    """The given set of packages create a stack."""


class HasVersion(EdgeBase):
    """The given package has a specific version."""


ALL_MODELS = frozenset((
    CreatesStack,
    DependsOn,
    HasVersion,
    IsPartOf,
    IsSolvedBy,
    Package,
    PythonPackageVersion,
    Requires,
    RPMPackageVersion,
    RPMRequirement,
    RuntimeEnvironment,
    SoftwareStack,
))
